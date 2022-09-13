import maya.cmds as cmds
import mgear.shifter.custom_step as cstp


class CustomShifterStep(cstp.customShifterMainStep):
    def __init__(self):
        self.name = "Reparent Pelvis Setup"

    def run(self, stepDict):
        print('Reparenting pelvis...')

        if cmds.objExists('pelvis') and cmds.objExists('root') and cmds.objExists('spine_C0_jnt_org') and cmds.objExists('cog_C0_ctlShape'):
            cmds.parent('pelvis', 'root')
            cmds.delete('spine_C0_jnt_org')

            cmds.setAttr('cog_C0_ctlShape.overrideColor', 20)
            print('Pelvis reparented.')
        else:
            print("Reparenting Pelvis unsuccessful. Objects don't exist.")
