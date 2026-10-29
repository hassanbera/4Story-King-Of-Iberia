#pragma once

#ifdef KOI_LOCAL_CLIENT
#include <stdio.h>

// Opt-in local development tool. Normal launches have no speed or recording change.
namespace LocalSurveyMode
{
    struct State
    {
        bool enabled, boost, recording, previousSpeedKey, previousRecordKey;
        DWORD lastSample, frameMilliseconds, event;
        FLOAT multiplier;
        HWND titleWindow;
        char csv[MAX_PATH];
        State() : enabled(false), boost(true), recording(true), previousSpeedKey(false),
            previousRecordKey(false), lastSample(0), frameMilliseconds(0), event(0), multiplier(1.0f), titleWindow(NULL)
        {
            char speed[16], directory[MAX_PATH];
            DWORD n = GetEnvironmentVariableA("KOI_SURVEY_SPEED", speed, sizeof(speed));
            if(!n || n >= sizeof(speed)) return;
            multiplier = FLOAT(atof(speed));
            if(!_finite(multiplier) || multiplier < 1.0f || multiplier > 3.0f) return;
            n = GetEnvironmentVariableA("KOI_SURVEY_DIR", directory, MAX_PATH);
            if(!n || n >= MAX_PATH - 20) return;
            DWORD attrs = GetFileAttributesA(directory);
            if(attrs == INVALID_FILE_ATTRIBUTES || !(attrs & FILE_ATTRIBUTE_DIRECTORY)) return;
            sprintf(csv, "%s\\walk.csv", directory);
            FILE *file = fopen(csv, "w");
            if(!file) return;
            fprintf(file, "tick_ms,map_id,x,y,z,ground_y,action,jump,fall,swim,ghost,dead,blocked,on_foot,focused,frame_ms,speed_setting,event,candidate\n");
            fclose(file);
            enabled = true;
        }
    };

    inline State &Get() { static State state; return state; }
    inline bool Enabled() { return Get().enabled; }
    inline bool Recording() { return Get().enabled && Get().recording; }

    inline void Title(HWND window)
    {
        State &s = Get();
        char title[128];
        sprintf(title, "4Story King Of Iberia - HARITALAMA %.0fx - KAYIT %s",
            s.boost ? s.multiplier : 1.0f, s.recording ? "ACIK" : "DURAKLATILDI");
        SetWindowTextA(window, title);
    }

    inline void BeginFrame(HWND window, DWORD milliseconds)
    {
        State &s = Get();
        if(!s.enabled) return;
        s.frameMilliseconds = milliseconds;
        bool foreground = GetForegroundWindow() == window;
        bool chord = foreground && (GetAsyncKeyState(VK_CONTROL) & 0x8000) && (GetAsyncKeyState(VK_SHIFT) & 0x8000);
        bool speed = chord && (GetAsyncKeyState(VK_F8) & 0x8000);
        bool record = chord && (GetAsyncKeyState(VK_F9) & 0x8000);
        bool changed = false;
        if(speed && !s.previousSpeedKey) { s.boost = !s.boost; ++s.event; changed = true; }
        if(record && !s.previousRecordKey) { s.recording = !s.recording; ++s.event; changed = true; }
        s.previousSpeedKey = speed;
        s.previousRecordKey = record;
        if(changed || s.titleWindow != window) { Title(window); s.titleWindow = window; }
    }

    struct ScopedSpeed
    {
        FLOAT &value;
        FLOAT original;
        ScopedSpeed(FLOAT &factor, bool onFoot) : value(factor), original(factor)
        {
            State &s = Get();
            if(s.enabled && s.boost && onFoot && s.frameMilliseconds <= 150)
                value = min(original * s.multiplier, TDEF_SPEED * 3.0f);
        }
        ~ScopedSpeed() { value = original; }
    };

    inline void Sample(HWND window, WORD map, const D3DXVECTOR3 &p, FLOAT ground,
        BYTE action, bool jump, bool fall, bool swim, bool ghost, bool dead, bool blocked, bool onFoot)
    {
        State &s = Get();
        if(!s.enabled || !s.recording) return;
        DWORD tick = GetTickCount();
        if(tick - s.lastSample < 60) return;
        s.lastSample = tick;
        bool focused = GetForegroundWindow() == window;
        bool candidate = focused && map == 0 && onFoot &&
            !jump && !fall && !swim && !ghost && !dead && !blocked &&
            s.frameMilliseconds <= 150 && _finite(p.x) && _finite(p.y) && _finite(p.z) &&
            _finite(ground) && fabs(p.y - ground) <= 1.0f;
        FILE *file = fopen(s.csv, "a");
        if(!file) return;
        fprintf(file, "%lu,%u,%.4f,%.4f,%.4f,%.4f,%u,%u,%u,%u,%u,%u,%u,%u,%u,%lu,%.1f,%lu,%u\n",
            tick, map, p.x, p.y, p.z, ground, action, unsigned(jump), unsigned(fall), unsigned(swim),
            unsigned(ghost), unsigned(dead), unsigned(blocked), unsigned(onFoot), unsigned(focused), s.frameMilliseconds,
            s.boost ? s.multiplier : 1.0f, s.event, unsigned(candidate));
        fclose(file);
    }
}
#endif
