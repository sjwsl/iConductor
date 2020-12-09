class Instrument:

    # @param name 乐器名称
    # @param r 极径
    # @param c 极角
    def __init__(self, name, r, c):
        self.name = name
        self.r = r
        self.c = c


class InstrumentContainer:
    def __init__(self):
        self.ilist = []

    # 每次加入，传一个乐器
    # @param instrument 加入的乐器
    def add(self, instrument):
        self.ilist += [instrument]

    # 每次加入，传一个乐器列表
    # @param instrument_list 要加入的乐器列表
    def create(self, instrument_dict):
        for ins in list(instrument_dict):
            r, c = instrument_dict[ins][0], instrument_dict[ins][1]
            instrument = Instrument(ins, r, c)
            self.add(instrument)

    # 每次搜索，传入极径、极角和存储结果列表
    # @param r 极径
    # @param c 极角
    def ask(self, r, c):
        ask_list = []
        for instrument in self.ilist:
            if instrument.c < c - 20 or instrument.c > c + 20:
                continue
            if instrument.r < r - 30 or instrument.r > r + 30:
                continue
            ask_list += [instrument.name]
        return ask_list


def test():
    instruments = [Instrument('1_钢琴', 70, 30),
                   Instrument('1_立式钢琴', 100, 160),
                   Instrument('2_钢琴', 100, 97),
                   Instrument('1_合成弦1', 70, 105)]
    container = InstrumentContainer()
    for instrument in instruments:
        container.add(instrument)
    ask_list = container.ask(90, 100)
    cnt = 0
    for s in ask_list:
        cnt = cnt + 1
        print(s, end='')
        if cnt == len(ask_list):
            print()
        else:
            print(", ", end='')


test()
