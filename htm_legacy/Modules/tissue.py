from Modules import master_values as mv

class distal_segment():
    def __init__(self, _synapses):
        self.actv_pot_syns = 0
        #array of synapses on segment [0(presynaptic cell), 1(permanance)]
        self.synapses = _synapses

class neuron():
    def __init__(self):
        self.d_segs = []

class n_column():

    def __init__(self):
        self.neurons = []
        self.p_synapses = {}
        self.active_duty = []
        self.activity = 0
        #self.is_active = False
        self.boost = 1
        self.overlap_s = 0

    def update_ADC(self, _self_active):
        if len(self.active_duty) > mv.act_duty_cycle:
            del self.active_duty[0]
        if _self_active:
            self.active_duty.append(1)
        else:
            self.active_duty.append(0)
        inhibit = 0
        for i in self.active_duty:
            if i == 1:
                inhibit += 1
        return inhibit

    #need to constrain and standardise boost(maybe dont let boost fall below 1??)
    #potential boost ; e^-b(self.activity-_mean_active)
        #where e is eulers cosstant and b is boosting factor (a master value parameter)
    def calculate_boost(self, _mean_active):
        self.boost = 1 + ((_mean_active - self.activity) / mv.act_duty_cycle)
        #print("ovrlp:", self.overlap_s, "S.A:", self.activity, "M.A:", _mean_active, "B:", self.boost)

    def reset(self):
        #self.is_active = False
        self.overlap_s = 0

    def update(self, _self_active, _mean_active):
        self.activity = self.update_ADC(_self_active)
        self.calculate_boost(_mean_active)
        self.reset()
