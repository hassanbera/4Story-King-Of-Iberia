"""Compile and run the local speed-scope check without a game or database."""
from pathlib import Path
import build_server


def main():
    root=Path(__file__).resolve().parents[1]
    output=root/'build/survey-tests';output.mkdir(parents=True,exist_ok=True)
    data=output/'data';data.mkdir(exist_ok=True)
    env=build_server.toolchain()
    binary=output/'survey_speed_smoke.exe'
    build_server.run('compile-survey-speed',['cl','/nologo','/MT','/EHsc',
        '/Fe'+str(binary),'/Fo'+str(output/'survey_speed_smoke.obj'),
        str(root/'tests/survey_speed_smoke.cpp'),'user32.lib'],output,env)
    build_server.run('test-survey-speed',[str(binary),str(data)],output,env)
    print((output/'test-survey-speed.log').read_text())


if __name__=='__main__':
    main()
