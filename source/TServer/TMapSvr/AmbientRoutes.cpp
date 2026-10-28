#include "StdAfx.h"
#include "AmbientRoutes.h"
#include <map>
#include <vector>
#include <stdio.h>
#include <math.h>

namespace
{
    struct Edge
    {
        WORD graphId;
        BYTE from;
        BYTE to;
    };

    struct Binding
    {
        WORD spawnId;
        WORD graphId;
    };

    struct Graph
    {
        WORD mapId;
        std::vector<AmbientRoutes::Node> nodes;
        std::vector<FLOAT> distance;
        std::vector<BYTE> nextHop;
        DWORD edgeCount;
        Graph() : mapId(0), edgeCount(0) {}
    };

    std::map<WORD, Graph> graphs;
    std::map<WORD, WORD> spawnGraphs;
    INIT_ONCE graphInit = INIT_ONCE_STATIC_INIT;
    const FLOAT unreachable = 1000000.0f;

    Graph *FindGraph(WORD graphId)
    {
        std::map<WORD, Graph>::iterator found = graphs.find(graphId);
        return found == graphs.end() ? NULL : &found->second;
    }

    BOOL CALLBACK LoadGraph(PINIT_ONCE, PVOID, PVOID *)
    {
        FILE *file = fopen("AmbientRoutes.csv", "rt");
        if(!file)
            return TRUE;

        std::vector<Edge> edges;
        std::vector<Binding> bindings;
        char line[256];
        BOOL valid = TRUE;
        while(valid && fgets(line, sizeof(line), file))
        {
            if(line[0] == '#' || line[0] == '\n' || line[0] == '\r')
                continue;
            unsigned graphId = 0, mapId = 0, id = 0, other = 0, probability = 0;
            FLOAT x = 0.0f, y = 0.0f, z = 0.0f, radius = 0.0f;
            if(line[0] == 'N' && sscanf(line, "N,%u,%u,%u,%f,%f,%f,%u,%f",
                &graphId, &mapId, &id, &x, &y, &z, &probability, &radius) == 8)
            {
                if(graphId == 0 || graphId > 65535 || mapId > 65535 || id > 199 || probability > 100 || radius < 0.0f || radius > 3.0f || !_finite(x) || !_finite(y) || !_finite(z))
                {
                    valid = FALSE;
                    break;
                }
                Graph &graph = graphs[WORD(graphId)];
                if(id != graph.nodes.size() || (id != 0 && graph.mapId != mapId))
                {
                    valid = FALSE;
                    break;
                }
                AmbientRoutes::Node node = {x, y, z, radius, BYTE(probability)};
                graph.mapId = WORD(mapId);
                graph.nodes.push_back(node);
            }
            else if(line[0] == 'E' && sscanf(line, "E,%u,%u,%u", &graphId, &id, &other) == 3)
            {
                if(graphId == 0 || graphId > 65535 || id > 199 || other > 199 || id == other)
                {
                    valid = FALSE;
                    break;
                }
                Edge edge = {WORD(graphId), BYTE(id), BYTE(other)};
                edges.push_back(edge);
            }
            else if(line[0] == 'R' && sscanf(line, "R,%u,%u", &id, &graphId) == 2)
            {
                if(id > 65535 || graphId == 0 || graphId > 65535)
                {
                    valid = FALSE;
                    break;
                }
                Binding binding = {WORD(id), WORD(graphId)};
                bindings.push_back(binding);
            }
            else
                valid = FALSE;
        }
        fclose(file);

        for(std::map<WORD, Graph>::iterator it = graphs.begin(); valid && it != graphs.end(); ++it)
        {
            Graph &graph = it->second;
            const size_t n = graph.nodes.size();
            if(n < 3 || n > 200)
            {
                valid = FALSE;
                break;
            }
            graph.distance.assign(n * n, unreachable);
            graph.nextHop.assign(n * n, 255);
            for(size_t i=0; i<n; ++i)
            {
                graph.distance[i*n+i] = 0.0f;
                graph.nextHop[i*n+i] = BYTE(i);
            }
        }

        for(size_t e=0; valid && e<edges.size(); ++e)
        {
            Graph *graph = FindGraph(edges[e].graphId);
            if(!graph || edges[e].from >= graph->nodes.size() || edges[e].to >= graph->nodes.size())
            {
                valid = FALSE;
                break;
            }
            const size_t n = graph->nodes.size();
            const size_t a = edges[e].from, b = edges[e].to;
            const AmbientRoutes::Node &first = graph->nodes[a], &second = graph->nodes[b];
            FLOAT dx = first.x - second.x, dz = first.z - second.z;
            FLOAT horizontal = sqrtf(dx*dx + dz*dz);
            FLOAT height = fabsf(first.y - second.y);
            if(horizontal > 40.0f || height > 12.0f)
            {
                valid = FALSE;
                break;
            }
            FLOAT cost = horizontal + height * 2.0f;
            if(cost < graph->distance[a*n+b])
            {
                graph->distance[a*n+b] = graph->distance[b*n+a] = cost;
                graph->nextHop[a*n+b] = BYTE(b);
                graph->nextHop[b*n+a] = BYTE(a);
                graph->edgeCount++;
            }
        }

        for(std::map<WORD, Graph>::iterator it = graphs.begin(); valid && it != graphs.end(); ++it)
        {
            Graph &graph = it->second;
            const size_t n = graph.nodes.size();
            for(size_t k=0; k<n; ++k)
                for(size_t i=0; i<n; ++i)
                    for(size_t j=0; j<n; ++j)
                    {
                        FLOAT candidate = graph.distance[i*n+k] + graph.distance[k*n+j];
                        if(candidate < graph.distance[i*n+j])
                        {
                            graph.distance[i*n+j] = candidate;
                            graph.nextHop[i*n+j] = graph.nextHop[i*n+k];
                        }
                    }
            for(size_t i=0; i<n*n; ++i)
                if(graph.distance[i] >= unreachable || graph.nextHop[i] == 255)
                    valid = FALSE;
        }

        for(size_t i=0; valid && i<bindings.size(); ++i)
        {
            if(!FindGraph(bindings[i].graphId) || spawnGraphs.find(bindings[i].spawnId) != spawnGraphs.end())
                valid = FALSE;
            else
                spawnGraphs[bindings[i].spawnId] = bindings[i].graphId;
        }
        if(bindings.empty() || graphs.empty())
            valid = FALSE;

        FILE *log = fopen("AmbientRoutes.load.log", "wt");
        if(log)
        {
            if(valid)
                for(std::map<WORD, Graph>::iterator it = graphs.begin(); it != graphs.end(); ++it)
                    fprintf(log, "graph=%u map=%u nodes=%u edges=%u connected=yes\n",
                        unsigned(it->first), unsigned(it->second.mapId), unsigned(it->second.nodes.size()), unsigned(it->second.edgeCount));
            else
                fprintf(log, "invalid route graph; ambient route fallback active\n");
            fclose(log);
        }
        if(!valid)
        {
            graphs.clear();
            spawnGraphs.clear();
        }
        return TRUE;
    }

    Graph *ReadyGraph(WORD graphId)
    {
        InitOnceExecuteOnce(&graphInit, LoadGraph, NULL, NULL);
        return FindGraph(graphId);
    }
}

WORD AmbientRoutes::GraphForSpawn(WORD mapId, WORD spawnId)
{
    InitOnceExecuteOnce(&graphInit, LoadGraph, NULL, NULL);
    std::map<WORD, WORD>::iterator it = spawnGraphs.find(spawnId);
    if(it == spawnGraphs.end())
        return 0;
    Graph *graph = FindGraph(it->second);
    return graph && graph->mapId == mapId ? it->second : 0;
}

BYTE AmbientRoutes::NodeCount(WORD mapId)
{
    Graph *graph = ReadyGraph(mapId);
    return graph ? BYTE(graph->nodes.size()) : 0;
}

const AmbientRoutes::Node *AmbientRoutes::GetNode(WORD mapId, BYTE nodeId)
{
    Graph *graph = ReadyGraph(mapId);
    return graph && nodeId < graph->nodes.size() ? &graph->nodes[nodeId] : NULL;
}

BYTE AmbientRoutes::NearestNode(WORD mapId, FLOAT x, FLOAT y, FLOAT z)
{
    Graph *graph = ReadyGraph(mapId);
    if(!graph)
        return 255;
    BYTE result = 255;
    FLOAT best = 1000000.0f;
    for(size_t i=0; i<graph->nodes.size(); ++i)
    {
        const Node &node = graph->nodes[i];
        FLOAT dx=x-node.x, dy=y-node.y, dz=z-node.z;
        FLOAT score=dx*dx+dz*dz+4.0f*dy*dy;
        if(score < best)
        {
            best=score;
            result=BYTE(i);
        }
    }
    return best <= 144.0f ? result : 255;
}

BYTE AmbientRoutes::ChooseDistantGoal(WORD mapId, BYTE fromNode)
{
    Graph *graph = ReadyGraph(mapId);
    if(!graph || fromNode >= graph->nodes.size())
        return 255;
    const size_t n=graph->nodes.size();
    FLOAT farthest=0.0f;
    for(size_t i=0; i<n; ++i)
        if(graph->distance[size_t(fromNode)*n+i] > farthest)
            farthest=graph->distance[size_t(fromNode)*n+i];
    const FLOAT threshold=farthest*0.55f;
    DWORD total=0;
    for(size_t i=0; i<n; ++i)
        if(i != fromNode && graph->distance[size_t(fromNode)*n+i] >= threshold)
            total += max(DWORD(1), DWORD(graph->distance[size_t(fromNode)*n+i]));
    if(!total)
        return 255;
    DWORD pick=((DWORD(rand()) << 15) ^ DWORD(rand())) % total;
    for(size_t i=0; i<n; ++i)
    {
        if(i == fromNode || graph->distance[size_t(fromNode)*n+i] < threshold)
            continue;
        DWORD weight=max(DWORD(1), DWORD(graph->distance[size_t(fromNode)*n+i]));
        if(pick < weight)
            return BYTE(i);
        pick -= weight;
    }
    return 255;
}

BYTE AmbientRoutes::NextHop(WORD mapId, BYTE fromNode, BYTE goalNode)
{
    Graph *graph = ReadyGraph(mapId);
    if(!graph || fromNode >= graph->nodes.size() || goalNode >= graph->nodes.size())
        return 255;
    return graph->nextHop[size_t(fromNode)*graph->nodes.size()+goalNode];
}
