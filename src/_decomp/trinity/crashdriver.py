#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\trinity\crashdriver.py
import blue
import trinity
import uthread2

def crash(done = None):
    rj = trinity.CreateRenderJob('Crash')
    rj.steps.append(trinity.TriStepRunComputeShader())
    rj.steps[0].effect = trinity.Tr2Effect()
    rj.steps[0].effect.effectFilePath = 'res:/graphics/effect/managed/space/system/crash.fx'
    blue.resMan.Wait()
    rj.ScheduleOnce()
    while not (rj.status == trinity.RJ_DONE or rj.status == trinity.RJ_FAILED or rj.cancelled):
        uthread2.yield_()

    if done:
        done[0] = True


def _main():
    from trinity.trinityapp import TrinityApp
    app = TrinityApp()
    done = [False]
    uthread2.start_tasklet(crash, done)
    while not done[0]:
        app.run_frames(10)


if __name__ == '__main__':
    _main()
