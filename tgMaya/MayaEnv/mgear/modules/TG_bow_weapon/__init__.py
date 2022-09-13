"""
Technically Games Bow and Arrow weapon module
"""
import maya.cmds as cmds
import pymel.core as pm
from itertools import product
from mgear.shifter import component
from mgear.core import attribute, primitive

angle_between_expression = "vector $vec_a = << .I[0], .I[1], .I[2] >>;\nvector $vec_b = << .I[3], .I[4], .I[5] >>;\n" \
                           "vector $vec_c = << .I[6], .I[7], .I[8] >>;\n$vec_ab = $vec_a - $vec_b;\n" \
                           "$vec_cb = $vec_c - $vec_b;\n$dot_ab_cb = dot($vec_ab, $vec_cb);\n" \
                           "$len_mul = mag($vec_ab) * mag($vec_cb);\nif($len_mul == 0)\n" \
                           "{\n\t$len_mul = $len_mul + 0.000001;\n}\n" \
                           ".O[0] = rad_to_deg(acos($dot_ab_cb/$len_mul));"


class Component(component.Main):

    def addObjects(self):
        self.grip_ik_cns = primitive.addTransform(self.root, self.getName('grip_ik_cns'), self.guide.tra['grip'])
        self.grip_ctl = self.addCtl(self.grip_ik_cns,
                                    'grip_ctl',
                                    self.guide.tra['grip'],
                                    self.color_ik,
                                    'cube',
                                    tp=self.parentCtlTag)

        attribute.setKeyableAttributes(self.grip_ctl,
                                       params=["tx", "ty", "tz",
                                               "ro", "rx", "ry", "rz"])

        self.aim_target = self.addCtl(self.grip_ctl,
                                      'aim_target_ctl',
                                      self.guide.tra['grip'],
                                      self.color_ik,
                                      'diamond',
                                      tp=self.parentCtlTag)

        # Top Arm
        self.arm_top_zero = primitive.addTransform(self.grip_ctl, self.getName('arm_top_zero'), self.guide.tra['arm_top'])
        self.arm_top = primitive.addTransform(self.arm_top_zero, self.getName('arm_top'), self.guide.tra['arm_top'])
        self.top_zero = primitive.addTransform(self.arm_top, self.getName('top_zero'), self.guide.tra['top'])
        self.top = primitive.addTransform(self.top_zero, self.getName('top'), self.guide.tra['top'])

        # Bottom Arm
        self.arm_bottom_zero = primitive.addTransform(self.grip_ctl, self.getName('arm_bottom_zero'), self.guide.tra['arm_bottom'])
        self.arm_bottom = primitive.addTransform(self.arm_bottom_zero, self.getName('arm_bottom'), self.guide.tra['arm_bottom'])
        self.bottom_zero = primitive.addTransform(self.arm_bottom, self.getName('bottom_zero'), self.guide.tra['bottom'])
        self.bottom = primitive.addTransform(self.bottom_zero, self.getName('bottom'), self.guide.tra['bottom'])

        # Sting Controller
        self.bowstring_ik_cns = primitive.addTransform(self.grip_ctl, self.getName('bowstring_ik_cns'), self.guide.tra['string'])
        self.bowstring_zero = primitive.addTransform(self.bowstring_ik_cns, self.getName('bowstring_zero'), self.guide.tra['string'])
        self.bowstring_ctl = self.addCtl(self.bowstring_zero,
                                         'bowstring_ctl',
                                         self.guide.tra['string'],
                                         self.color_ik,
                                         'diamond',
                                         tp=self.grip_ctl)

        attribute.setKeyableAttributes(self.bowstring_ctl,
                                       params=["tx", "ty", "tz",
                                               "ro", "rx", "ry", "rz"])

        self.bowstring_grp = primitive.addTransform(self.bowstring_ctl, self.getName('bowstring_grp'), self.guide.tra['string'])

        # Arrow
        self.arrow_ik_cns = primitive.addTransform(self.root, self.getName('arrow_ik_cns'), self.guide.tra['arrow'])
        self.arrow_placement = self.addCtl(self.arrow_ik_cns,
                                           'arrow_placement_ctl',
                                           self.guide.tra['arrow'],
                                           self.color_ik,
                                           'diamond',
                                           tp=self.parentCtlTag)
        self.arrow_zero = primitive.addTransform(self.arrow_placement, self.getName('arrow_zero'), self.guide.tra['arrow'])
        self.arrow_ctl = self.addCtl(self.arrow_zero,
                                     'arrow_ctl',
                                     self.guide.tra['arrow'],
                                     self.color_ik,
                                     'circle',
                                     tp=self.parentCtlTag)

        attribute.setKeyableAttributes(self.arrow_ctl,
                                       params=["tx", "ty", "tz",
                                               "ro", "rx", "ry", "rz"])

        rotOderList = ["XYZ", "YZX", "ZXY", "XZY", "YXZ", "ZYX"]
        attribute.setRotOrder(self.grip_ctl, rotOderList[self.settings["grip_rotorder"]])
        attribute.setRotOrder(self.bowstring_ctl, rotOderList[self.settings["grip_rotorder"]])
        attribute.setRotOrder(self.arrow_ctl, rotOderList[self.settings["grip_rotorder"]])

        self.jnt_pos.append([self.grip_ctl, 'grip', 'parent_relative_jnt', True])
        self.jnt_pos.append([self.arm_top, 'arm_top', 'grip', True])
        self.jnt_pos.append([self.top, 'top', 'arm_top', True])
        self.jnt_pos.append([self.arm_bottom, 'arm_bottom', 'grip', True])
        self.jnt_pos.append([self.bottom, 'bottom', 'arm_bottom', True])
        self.jnt_pos.append([self.bowstring_grp, 'bowstring', 'grip', True])
        self.jnt_pos.append([self.arrow_ctl, 'arrow', 'grip', True])

    def addAttributes(self):
        self.grip_ikref_att = None
        self.string_ikref_att = None
        self.arrow_ikref_att = None

        if self.settings['grip_ikref_array']:
            grip_ref_names = self.get_valid_alias_list(self.settings["grip_ikref_array"].split(","))
            if len(grip_ref_names) > 1:
                self.grip_ikref_att = self.addAnimEnumParam("gripikref", "Grip Ik Ref", 0, grip_ref_names)

        if self.settings['string_ikref_array']:
            string_ref_names = self.get_valid_alias_list(self.settings["string_ikref_array"].split(","))
            if len(string_ref_names) > 1:
                self.string_ikref_att = self.addAnimEnumParam("stringikref", "Bowstring Ik Ref", 0, string_ref_names)

        if self.settings['arrow_ikref_array']:
            arrow_ref_names = self.get_valid_alias_list(self.settings["arrow_ikref_array"].split(","))
            if len(arrow_ref_names) > 1:
                self.arrow_ikref_att = self.addAnimEnumParam("arrowikref", "Arrow Ik Ref", 0, arrow_ref_names)

        self.tension_attr = self.addAnimParam('tension', 'Tension', 'float', .5, 0, 1)
        self.flexibility_attr = self.addAnimParam('flexibility', 'Flexibility', 'float', 1)
        self.arrow_aim_attr = self.addAnimParam('arrow_aim', 'Arrow Aim', 'bool', False)

    def addOperators(self):
        # Top Arm Aiming
        top_aim_matrix = cmds.createNode('aimMatrix', name=self.getName('top_aimMatrix'))
        top_mult_mat = cmds.createNode('multMatrix', name=self.getName('top_multMatrix'))
        top_inverse_mat = cmds.createNode('inverseMatrix', name=self.getName('top_inverseMatrix'))
        top_decompose_mat = cmds.createNode('decomposeMatrix', name=self.getName('top_decomposeMatrix'))

        cmds.setAttr('{}.primaryInputAxis'.format(top_aim_matrix), 0, -1, 0, type='double3')
        cmds.setAttr('{}.secondaryInputAxis'.format(top_aim_matrix), 0, 0, 0, type='double3')
        cmds.setAttr('{}.secondaryTargetVector'.format(top_aim_matrix), 1, 0, 0, type='double3')
        cmds.setAttr('{}.secondaryMode'.format(top_aim_matrix), 1)

        cmds.connectAttr('{}.worldMatrix[0]'.format(self.top_zero.longName()), '{}.inputMatrix'.format(top_aim_matrix))
        cmds.connectAttr('{}.worldMatrix[0]'.format(self.bowstring_grp.longName()), '{}.primaryTargetMatrix'.format(top_aim_matrix))

        cmds.connectAttr('{}.outputMatrix'.format(top_aim_matrix), '{}.matrixIn[0]'.format(top_mult_mat))
        cmds.connectAttr('{}.worldMatrix[0]'.format(self.arm_top_zero.longName()), '{}.inputMatrix'.format(top_inverse_mat))
        cmds.connectAttr('{}.outputMatrix'.format(top_inverse_mat), '{}.matrixIn[1]'.format(top_mult_mat))

        cmds.connectAttr('{}.matrixSum'.format(top_mult_mat), '{}.inputMatrix'.format(top_decompose_mat))
        cmds.connectAttr('{}.outputRotate'.format(top_decompose_mat), '{}.rotate'.format(self.top.longName()))

        # Bottom Arm Aiming
        bottom_aim_matrix = cmds.createNode('aimMatrix', name=self.getName('bottom_aimMatrix'))
        bottom_mult_mat = cmds.createNode('multMatrix', name=self.getName('bottom_multMatrix'))
        bottom_inverse_mat = cmds.createNode('inverseMatrix', name=self.getName('bottom_inverseMatrix'))
        bottom_decompose_mat = cmds.createNode('decomposeMatrix', name=self.getName('bottom_decomposeMatrix'))

        cmds.setAttr('{}.primaryInputAxis'.format(bottom_aim_matrix), 0, 1, 0, type='double3')
        cmds.setAttr('{}.secondaryInputAxis'.format(bottom_aim_matrix), 0, 0, 0, type='double3')
        cmds.setAttr('{}.secondaryTargetVector'.format(bottom_aim_matrix), 1, 0, 0, type='double3')
        cmds.setAttr('{}.secondaryMode'.format(bottom_aim_matrix), 1)

        cmds.connectAttr('{}.worldMatrix[0]'.format(self.bottom_zero.longName()), '{}.inputMatrix'.format(bottom_aim_matrix))
        cmds.connectAttr('{}.worldMatrix[0]'.format(self.bowstring_grp.longName()), '{}.primaryTargetMatrix'.format(bottom_aim_matrix))

        cmds.connectAttr('{}.outputMatrix'.format(bottom_aim_matrix), '{}.matrixIn[0]'.format(bottom_mult_mat))
        cmds.connectAttr('{}.worldMatrix[0]'.format(self.arm_bottom.longName()), '{}.inputMatrix'.format(bottom_inverse_mat))
        cmds.connectAttr('{}.outputMatrix'.format(bottom_inverse_mat), '{}.matrixIn[1]'.format(bottom_mult_mat))

        cmds.connectAttr('{}.matrixSum'.format(bottom_mult_mat), '{}.inputMatrix'.format(bottom_decompose_mat))
        cmds.connectAttr('{}.outputRotate'.format(bottom_decompose_mat), '{}.rotate'.format(self.bottom.longName()))

        # Tension General
        grip_ctl_decomp = cmds.createNode('decomposeMatrix', name=self.getName('grip_decomposeMatrix'))
        bowstring_decomp = cmds.createNode('decomposeMatrix', name=self.getName('bowstring_decomposeMatrix'))
        cmds.connectAttr('{}.worldMatrix[0]'.format(self.grip_ctl.longName()), '{}.inputMatrix'.format(grip_ctl_decomp))
        cmds.connectAttr('{}.worldMatrix[0]'.format(self.bowstring_grp.longName()), '{}.inputMatrix'.format(bowstring_decomp))

        # Top Tension
        arm_top_decomp = cmds.createNode('decomposeMatrix', name=self.getName('arm_top_decomposeMatrix'))
        cmds.connectAttr('{}.worldMatrix[0]'.format(self.arm_top_zero.longName()), '{}.inputMatrix'.format(arm_top_decomp))

        top_tension_exp = cmds.createNode('expression', name=self.getName('top_expression'))
        cmds.expression(top_tension_exp, e=True, string=angle_between_expression, alwaysEvaluate=0)
        nodes = ','.join([grip_ctl_decomp, arm_top_decomp, bowstring_decomp])
        plugs = ','.join(['.outputTranslateX', '.outputTranslateY', '.outputTranslateZ'])
        node_plugs = [node + plug for node, plug in product(nodes.split(','), plugs.split(','))]
        for ind, plug in enumerate(node_plugs):
            cmds.connectAttr('{}'.format(plug), '{}.input[{}]'.format(top_tension_exp, ind))

        arm_top_tension_rest_angle = cmds.createNode('floatConstant', name=self.getName('arm_top_rest_floatConstant'))
        cmds.setAttr('{}.inFloat'.format(arm_top_tension_rest_angle), cmds.getAttr('{}.output[0]'.format(top_tension_exp)))

        arm_top_angle_diff = cmds.createNode('plusMinusAverage', name=self.getName('arm_top_angle_diff_plusMinusAverage'))
        cmds.setAttr('{}.operation'.format(arm_top_angle_diff), 2)
        cmds.connectAttr('{}.outFloat'.format(arm_top_tension_rest_angle), '{}.input1D[0]'.format(arm_top_angle_diff))
        cmds.connectAttr('{}.output[0]'.format(top_tension_exp), '{}.input1D[1]'.format(arm_top_angle_diff))

        arm_top_tension = cmds.createNode('multiplyDivide', name=self.getName('arm_top_tension_multiplyDivide'))
        cmds.setAttr('{}.operation'.format(arm_top_tension), 1)
        cmds.connectAttr('{}.output1D'.format(arm_top_angle_diff), '{}.input1X'.format(arm_top_tension))
        cmds.connectAttr('{}'.format(self.tension_attr), '{}.input2X'.format(arm_top_tension))

        arm_top_flexibility = cmds.createNode('multiplyDivide', name=self.getName('arm_top_flexibility_multiplyDivide'))
        cmds.setAttr('{}.operation'.format(arm_top_flexibility), 1)
        cmds.connectAttr('{}.outputX'.format(arm_top_tension), '{}.input1X'.format(arm_top_flexibility))
        cmds.connectAttr('{}'.format(self.flexibility_attr), '{}.input2X'.format(arm_top_flexibility))

        cmds.connectAttr('{}.outputX'.format(arm_top_flexibility), '{}.rotateX'.format(self.arm_top.longName()))

        # Bottom Tension
        arm_bottom_decomp = cmds.createNode('decomposeMatrix', name=self.getName('arm_bottom_decomposeMatrix'))
        cmds.connectAttr('{}.worldMatrix[0]'.format(self.arm_bottom_zero.longName()), '{}.inputMatrix'.format(arm_bottom_decomp))

        bottom_tension_exp = cmds.createNode('expression', name=self.getName('bottom_expression'))
        cmds.expression(bottom_tension_exp, e=True, string=angle_between_expression, alwaysEvaluate=0)
        nodes = ','.join([grip_ctl_decomp, arm_bottom_decomp, bowstring_decomp])
        plugs = ','.join(['.outputTranslateX', '.outputTranslateY', '.outputTranslateZ'])
        node_plugs = [node + plug for node, plug in product(nodes.split(','), plugs.split(','))]
        for ind, plug in enumerate(node_plugs):
            cmds.connectAttr('{}'.format(plug), '{}.input[{}]'.format(bottom_tension_exp, ind))

        arm_bottom_tension_rest_angle = cmds.createNode('floatConstant', name=self.getName('arm_bottom_rest_floatConstant'))
        cmds.setAttr('{}.inFloat'.format(arm_bottom_tension_rest_angle), cmds.getAttr('{}.output[0]'.format(bottom_tension_exp)))

        arm_bottom_angle_diff = cmds.createNode('plusMinusAverage', name=self.getName('arm_bottom_angle_diff_plusMinusAverage'))
        cmds.setAttr('{}.operation'.format(arm_bottom_angle_diff), 2)
        cmds.connectAttr('{}.output[0]'.format(bottom_tension_exp), '{}.input1D[0]'.format(arm_bottom_angle_diff))
        cmds.connectAttr('{}.outFloat'.format(arm_bottom_tension_rest_angle), '{}.input1D[1]'.format(arm_bottom_angle_diff))

        arm_bottom_tension = cmds.createNode('multiplyDivide', name=self.getName('arm_bottom_tension_multiplyDivide'))
        cmds.setAttr('{}.operation'.format(arm_bottom_tension), 1)
        cmds.connectAttr('{}.output1D'.format(arm_bottom_angle_diff), '{}.input1X'.format(arm_bottom_tension))
        cmds.connectAttr('{}'.format(self.tension_attr), '{}.input2X'.format(arm_bottom_tension))

        arm_bottom_flexibility = cmds.createNode('multiplyDivide', name=self.getName('arm_bottom_flexibility_multiplyDivide'))
        cmds.setAttr('{}.operation'.format(arm_bottom_flexibility), 1)
        cmds.connectAttr('{}.outputX'.format(arm_bottom_tension), '{}.input1X'.format(arm_bottom_flexibility))
        cmds.connectAttr('{}'.format(self.flexibility_attr), '{}.input2X'.format(arm_bottom_flexibility))

        cmds.connectAttr('{}.outputX'.format(arm_bottom_flexibility), '{}.rotateX'.format(self.arm_bottom.longName()))

        # Arrow Aim
        arrow_aim_matrix = cmds.createNode('aimMatrix', name=self.getName('arrow_aimMatrix'))
        arrow_mult_mat = cmds.createNode('multMatrix', name=self.getName('arrow_multMatrix'))
        arrow_inverse_mat = cmds.createNode('inverseMatrix', name=self.getName('arrow_inverseMatrix'))
        arrow_decompose_mat = cmds.createNode('decomposeMatrix', name=self.getName('arrow_decomposeMatrix'))

        cmds.setAttr('{}.primaryInputAxis'.format(arrow_aim_matrix), 1, 0, 0, type='double3')
        cmds.setAttr('{}.secondaryInputAxis'.format(arrow_aim_matrix), 0, 1, 0, type='double3')
        cmds.setAttr('{}.secondaryTargetVector'.format(arrow_aim_matrix), 0, 0, 0, type='double3')
        cmds.setAttr('{}.secondaryMode'.format(arrow_aim_matrix), 1)

        cmds.connectAttr('{}.worldMatrix[0]'.format(self.arrow_placement.longName()), '{}.inputMatrix'.format(arrow_aim_matrix))
        cmds.connectAttr('{}.worldMatrix[0]'.format(self.aim_target.longName()), '{}.primaryTargetMatrix'.format(arrow_aim_matrix))

        cmds.connectAttr('{}.outputMatrix'.format(arrow_aim_matrix), '{}.matrixIn[0]'.format(arrow_mult_mat))
        cmds.connectAttr('{}.worldMatrix[0]'.format(self.arrow_placement.longName()), '{}.inputMatrix'.format(arrow_inverse_mat))
        cmds.connectAttr('{}.outputMatrix'.format(arrow_inverse_mat), '{}.matrixIn[1]'.format(arrow_mult_mat))

        cmds.connectAttr('{}.matrixSum'.format(arrow_mult_mat), '{}.inputMatrix'.format(arrow_decompose_mat))

        arrow_choice_node = cmds.createNode('choice', name=self.getName('arrow_Choice'))
        arrow_decompose_mat_1 = cmds.createNode('decomposeMatrix', name=self.getName('arrow_decomposeMatrix1'))
        cmds.setAttr('{}.inputMatrix'.format(arrow_decompose_mat_1), cmds.xform(self.arrow_ctl.longName(), ws=True, m=True, q=True), type='matrix')
        cmds.connectAttr('{}.outputRotate'.format(arrow_decompose_mat_1), '{}.input[0]'.format(arrow_choice_node))
        cmds.connectAttr('{}.outputRotate'.format(arrow_decompose_mat), '{}.input[1]'.format(arrow_choice_node))
        cmds.connectAttr('{}'.format(self.arrow_aim_attr), '{}.selector'.format(arrow_choice_node))

        cmds.connectAttr('{}.output'.format(arrow_choice_node), '{}.rotate'.format(self.arrow_zero.longName()))

    def setRelation(self):
        self.relatives['root'] = self.grip_ctl
        self.relatives['grip'] = self.grip_ctl
        self.relatives['string'] = self.bowstring_ctl
        self.relatives['arrow'] = self.arrow_ctl

        self.controlRelatives['root'] = self.grip_ctl
        self.controlRelatives['grip'] = self.grip_ctl
        self.controlRelatives['string'] = self.bowstring_ctl
        self.controlRelatives['arrow'] = self.arrow_ctl

        self.jointRelatives['root'] = 0
        self.jointRelatives['grip'] = 0
        self.jointRelatives['arm_top'] = 1
        self.jointRelatives['top'] = 2
        self.jointRelatives['arm_bottom'] = 3
        self.jointRelatives['bottom'] = 4
        self.jointRelatives['string'] = 5
        self.jointRelatives['arrow'] = 6

        self.aliasRelatives['root'] = 'grip_ctl'
        self.aliasRelatives['grip'] = 'grip_ctl'
        self.aliasRelatives['string'] = 'bowstring_ctl'
        self.aliasRelatives['arrow'] = 'arrow_ctl'

    def addConnection(self):
        """Add more connection definition to the set"""
        self.connections["standard"] = self.connect_standard

    def connect_standard(self):
        self.parent.addChild(self.root)
        if self.grip_ikref_att is not None:
            self.connectRef2(self.settings['grip_ikref_array'], self.grip_ik_cns, self.grip_ikref_att)
        if self.string_ikref_att is not None:
            self.connectRef2(self.settings['string_ikref_array'], self.bowstring_ik_cns, self.string_ikref_att)
        if self.arrow_ikref_att is not None:
            self.connectRef2(self.settings['arrow_ikref_array'], self.arrow_ik_cns, self.arrow_ikref_att)

