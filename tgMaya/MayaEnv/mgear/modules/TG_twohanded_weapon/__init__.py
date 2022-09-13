"""
Technically Games Two-handed weapon module
"""

from mgear.shifter import component
from mgear.core import attribute, primitive


class Component(component.Main):
    """Shifter component Class"""

    # =====================================================
    # OBJECTS
    # =====================================================
    def addObjects(self):
        """Add all the objects needed to create the component."""

        self.ik_cns = primitive.addTransform(self.root, self.getName("ik_cns"), self.guide.tra['top'])

        self.top_ctl = self.addCtl(self.ik_cns,
                                   'top_ctl',
                                   self.guide.tra['top'],
                                   self.color_ik,
                                   'diamond',
                                   w=5,
                                   h=5,
                                   d=5,
                                   tp=self.parentCtlTag)

        self.mid_zero = primitive.addTransform(self.top_ctl, self.getName("mid_zero"), self.guide.tra['mid'])

        self.mid_ctl = self.addCtl(self.mid_zero,
                                   'mid_ctl',
                                   self.guide.tra['mid'],
                                   self.color_ik,
                                   'cube',
                                   w=5,
                                   h=5,
                                   d=5,
                                   tp=self.top_ctl)

        self.bot_zero = primitive.addTransform(self.mid_ctl, self.getName("bottom_zero"), self.guide.tra['bottom'])

        self.bot_ctl = self.addCtl(self.bot_zero,
                                   'bottom_ctl',
                                   self.guide.tra['bottom'],
                                   self.color_ik,
                                   'diamond',
                                   w=5,
                                   h=5,
                                   d=5,
                                   tp=self.mid_ctl)

        attribute.setKeyableAttributes(self.top_ctl,
                                       params=["tx", "ty", "tz",
                                               "ro", "rx", "ry", "rz"])

        attribute.setKeyableAttributes(self.mid_ctl,
                                       params=["tx", "ty", "tz",
                                               "ro", "rx", "ry", "rz"])

        attribute.setKeyableAttributes(self.bot_ctl,
                                       params=["tx", "ty", "tz",
                                               "ro", "rx", "ry", "rz"])

        rotOderList = ["XYZ", "YZX", "ZXY", "XZY", "YXZ", "ZYX"]
        attribute.setRotOrder(self.top_ctl, rotOderList[self.settings["top_rotorder"]])
        attribute.setRotOrder(self.mid_ctl, rotOderList[self.settings["mid_rotorder"]])
        attribute.setRotOrder(self.bot_ctl, rotOderList[self.settings["bot_rotorder"]])

        if self.settings["top_joint"]:
            self.jnt_pos.append(
                [self.top_ctl, self.name, None, True])
        if self.settings["mid_joint"]:
            self.jnt_pos.append(
                [self.mid_ctl, self.name, None, True])
        if self.settings["bot_joint"]:
            self.jnt_pos.append(
                [self.bot_ctl, self.name, None, True])

    def addAttributes(self):
        # Ref
        if self.settings["top_ikref_array"]:
            ref_names = self.get_valid_alias_list(self.settings["top_ikref_array"].split(","))
            if len(ref_names) > 1:
                self.ikref_att = self.addAnimEnumParam("ikref", "Ik Ref", 0, ref_names)

    def addOperators(self):
        return

    # =====================================================
    # CONNECTOR
    # =====================================================
    def setRelation(self):
        """Set the relation beetween object from guide to rig"""
        self.relatives['root'] = self.top_ctl
        self.relatives['top'] = self.top_ctl
        self.relatives['mid'] = self.mid_ctl
        self.relatives['bottom'] = self.bot_ctl

        self.controlRelatives['root'] = self.top_ctl
        self.controlRelatives['top'] = self.top_ctl
        self.controlRelatives['mid'] = self.mid_ctl
        self.controlRelatives['bottom'] = self.bot_ctl

        jnt_ind = 0
        if self.settings["top_joint"]:
            self.jointRelatives['root'] = jnt_ind
            self.jointRelatives['top'] = jnt_ind
            jnt_ind += 1
        if self.settings['mid_joint']:
            self.jointRelatives['mid'] = jnt_ind
            jnt_ind += 1
        if self.settings['bot_joint']:
            self.jointRelatives['bot'] = jnt_ind

        self.aliasRelatives['root'] = 'top_ctl'
        self.aliasRelatives['top'] = 'top_ctl'
        self.aliasRelatives['mid'] = 'mid_ctl'
        self.aliasRelatives['bottom'] = 'bottom_ctl'

    def addConnection(self):
        """Add more connection definition to the set"""
        self.connections["standard"] = self.connect_standard

    def connect_standard(self):
        self.parent.addChild(self.root)
        self.connectRef(self.settings['top_ikref_array'], self.ik_cns)
