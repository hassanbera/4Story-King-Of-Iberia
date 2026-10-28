#pragma once

// Immutable resident-bound route graphs loaded from AmbientRoutes.csv.
// Node IDs 0..199 fit in the existing monster waypoint byte.
namespace AmbientRoutes
{
    struct Node
    {
        FLOAT x;
        FLOAT y;
        FLOAT z;
        FLOAT radius;
        BYTE stopProbability;
    };

    WORD GraphForSpawn(WORD mapId, WORD spawnId);
    BYTE NodeCount(WORD graphId);
    const Node *GetNode(WORD graphId, BYTE nodeId);
    BYTE NearestNode(WORD graphId, FLOAT x, FLOAT y, FLOAT z);
    BYTE ChooseDistantGoal(WORD graphId, BYTE fromNode);
    BYTE NextHop(WORD graphId, BYTE fromNode, BYTE goalNode);
}
