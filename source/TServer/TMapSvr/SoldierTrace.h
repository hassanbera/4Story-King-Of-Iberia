#pragma once
#include <stdio.h>
#include <stdarg.h>

// Local spawn/route diagnostics only; no account or packet contents.
inline void SoldierTrace(const char *format, ...)
{
    char filename[MAX_PATH];
    GetModuleFileNameA(NULL, filename, MAX_PATH);
    char *slash = strrchr(filename, '\\');
    if(!slash) return;
    strcpy(slash + 1, "SoldierRoute.log");
    FILE *file = fopen(filename, "a");
    if(!file) return;
    fprintf(file, "tick=%lu ", GetTickCount());
    va_list args;
    va_start(args, format);
    vfprintf(file, format, args);
    va_end(args);
    fprintf(file, "\n");
    fclose(file);
}
