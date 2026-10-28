#pragma once
#include <stdio.h>

// Explicit local walk capture, enabled only by a marker beside the Map binary.
// Records map coordinates, never credentials or chat.
inline void RecordRouteSurvey(WORD mapID, FLOAT x, FLOAT y, FLOAT z)
{
    if(mapID != 0 || x < 5300 || x > 5530 || z < 4600 || z > 4820) return;
    static DWORD lastSample = 0;
    DWORD now = GetTickCount();
    if(now - lastSample < 250) return;
    lastSample = now;
    char filename[MAX_PATH];
    GetModuleFileNameA(NULL, filename, MAX_PATH);
    char *slash = strrchr(filename, '\\');
    if(!slash) return;
    strcpy(slash + 1, "RouteSurvey.enabled");
    if(GetFileAttributesA(filename) == INVALID_FILE_ATTRIBUTES) return;
    strcpy(slash + 1, "RouteSurvey.csv");
    FILE *file = fopen(filename, "a");
    if(!file) return;
    fprintf(file, "%lu,%u,%.4f,%.4f,%.4f\n", now, mapID, x, y, z);
    fclose(file);
}
