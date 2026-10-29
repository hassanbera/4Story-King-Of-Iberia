#define KOI_LOCAL_CLIENT
#include <windows.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <float.h>
#include <assert.h>
struct D3DXVECTOR3 { float x,y,z; };
#define TDEF_SPEED 0.9f
#include "../source/TClient/TClient/LocalSurveyMode.h"

int main(int argc,char **argv)
{
    if(argc!=2) return 2;
    SetEnvironmentVariableA("KOI_SURVEY_SPEED",NULL);
    LocalSurveyMode::State normal;
    assert(!normal.enabled);
    SetEnvironmentVariableA("KOI_SURVEY_SPEED","3");
    SetEnvironmentVariableA("KOI_SURVEY_DIR",argv[1]);
    LocalSurveyMode::State &state=LocalSurveyMode::Get();
    assert(state.enabled);
    state.frameMilliseconds=16;
    float speed=TDEF_SPEED;
    { LocalSurveyMode::ScopedSpeed scope(speed,true); assert(fabs(speed-TDEF_SPEED*3)<.00001f); }
    assert(speed==TDEF_SPEED);
    { LocalSurveyMode::ScopedSpeed scope(speed,false); assert(speed==TDEF_SPEED); }
    state.frameMilliseconds=200;
    { LocalSurveyMode::ScopedSpeed scope(speed,true); assert(speed==TDEF_SPEED); }
    state.frameMilliseconds=16;state.boost=false;
    { LocalSurveyMode::ScopedSpeed scope(speed,true); assert(speed==TDEF_SPEED); }
    state.boost=true;speed=1.5f;
    { LocalSurveyMode::ScopedSpeed scope(speed,true); assert(fabs(speed-TDEF_SPEED*3)<.00001f); }
    assert(speed==1.5f);
    puts("Survey speed cap, normal mode, non-foot exclusion, low-FPS exclusion and restoration passed.");
    return 0;
}
