"""
Technically Games chain module
"""

import maya.cmds as cmds
from pymel.core import datatypes
from mgear.shifter import component
from mgear.core import primitive, transform, vector


class Component(component.Main):
    """
    Shifter component class for the TG Chain module
    """

    def addObjects(self):
        self.normal = self.guide.blades['blade'].z
        self.binormal = self.guide. blades['blade'].x

        self.WIP = self.options['mode']

        if self.negate and self.settings['overrideNegate']:
            self.negate = False
            self.n_factor = 1

        if self.settings['overrideNegate']:
            self.mirror_conf = [0, 0, 1,
                                1, 1, 0,
                                0, 0, 0]
        else:
            self.mirror_conf = [0, 0, 0,
                                0, 0, 0,
                                0, 0, 0]

        self.fk_npo = []
        self.fk_ctl = []
        # t = self.guide.tra['root']

        parent = self.root
        t_old = False

        self.previous_tag = self.parentCtlTag

        self.master_npo = None
        self.master_ctl = None

        for i, t in enumerate(transform.getChainTransform(self.guide.apos, self.normal, self.negate)):
            dist = vector.getDistance(self.guide.apos[i], self.guide.apos[i + 1])

            if self.settings['neutralpose'] or not t_old:
                t_npo = t
            else:
                t_npo = transform.setMatrixPosition(t_old, transform.getPositionFromMatrix(t))

            if i == 0:
                self.master_offset = primitive.addTransform(parent, self.getName('fk_master_offset'), t_npo)
                self.master_npo = primitive.addTransform(self.master_offset, self.getName("fk_master_npo"), t_npo)
                self.master_ctl = self.addCtl(self.master_npo,
                                              'fk_master_ctl',
                                              t_npo,
                                              self.color_ik,
                                              'cross',
                                              degree=3,
                                              tp=self.previous_tag,
                                              ro=datatypes.Vector(datatypes.pi/2, datatypes.pi/4, 0),
                                              mirrorConf=self.mirror_conf)
                parent = self.master_ctl

            fk_offset = primitive.addTransform(parent, self.getName("fk%s_offset" % i), t_npo)
            fk_npo = primitive.addTransform(fk_offset, self.getName("fk%s_npo" % i), t_npo)
            fk_ctl = self.addCtl(fk_npo,
                                 'fk%s_ctl' % i,
                                 t,
                                 self.color_fk,
                                 'circle',
                                 w=dist,
                                 degree=3,
                                 h=self.size * .1,
                                 d=self.size * .1,
                                 po=datatypes.Vector(dist * .5 * self.n_factor, 0, 0),
                                 tp=self.previous_tag,
                                 mirrorConf=self.mirror_conf)
            self.fk_npo.append(fk_npo)
            self.fk_ctl.append(fk_ctl)
            t_old = t
            self.previous_tag = fk_ctl
            parent = fk_ctl

            if self.settings['addJoints']:
                jnt_name = '_'.join([self.name, str(i + 1).zfill(2)])
                self.jnt_pos.append([fk_ctl, jnt_name, None, False])

    def addAttributes(self):
        return

    def addOperators(self):
        for fk_npo in self.fk_npo[1:]:
            for axis in ['X', 'Y', 'Z']:
                cmds.connectAttr('{}.rotate{}'.format(self.master_ctl.longName(), axis),
                                 '{}.rotate{}'.format(fk_npo.longName(), axis))

    def setRelation(self):
        self.relatives["root"] = self.fk_ctl[0]
        self.controlRelatives["root"] = self.fk_ctl[0]
        self.jointRelatives["root"] = 0
        for i in range(0, len(self.fk_ctl) - 1):
            self.relatives["%s_loc" % i] = self.fk_ctl[i + 1]
            self.controlRelatives["%s_loc" % i] = self.fk_ctl[i + 1]
            self.jointRelatives["%s_loc" % i] = i + 1
            self.aliasRelatives["%s_ctl" % i] = i + 1
        self.relatives["%s_loc" % (len(self.fk_ctl) - 1)] = self.fk_ctl[-1]
        self.controlRelatives["%s_loc" % (
                len(self.fk_ctl) - 1)] = self.fk_ctl[-1]
        self.jointRelatives["%s_loc" % (
                len(self.fk_ctl) - 1)] = len(self.fk_ctl) - 1
        self.aliasRelatives["%s_loc" % (
                len(self.fk_ctl) - 1)] = len(self.fk_ctl) - 1
