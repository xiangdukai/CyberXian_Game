from flask_sqlalchemy import SQLAlchemy
import time
import random

db = SQLAlchemy()


class Character(db.Model):
    __tablename__ = 'characters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    spirit_power = db.Column(db.Integer, default=0)
    cultivation_talent = db.Column(db.Integer, default=0)
    combat_talent = db.Column(db.Integer, default=0)
    practice_count = db.Column(db.Integer, default=0)
    rebirth_opportunity = db.Column(db.Integer, default=0)
    last_action_time = db.Column(db.Float, default=0)
    realm = db.Column(db.String(80), default='开元前期')
    nickname = db.Column(db.String(80), default='')
    password = db.Column(db.String(100), nullable=False)
    

    def __init__(self, name, password, spirit_power=0):
        self.name = name
        self.password = password  # 设置密码
        self.spirit_power = 0  # 初始灵力
        self.cultivation_talent = self.generate_talent()  # 生成修炼天赋
        self.combat_talent = self.generate_talent()  # 生成战斗天赋
        self.practice_count = 0
        self.rebirth_opportunity = 0
        self.last_action_time = 0
        self.realm = '开元前期'
        self.nickname = '狗屎' if name == "郑鑫国" else ''  # 郑鑫国的特殊昵称
        

    def practice(self):
        current_time = time.time()
        if current_time - self.last_action_time >= 1:
            self.spirit_power += self.cultivation_talent
            self.practice_count += 1
            self.update_realm()
            self.last_action_time = current_time

            if self.practice_count % 100 == 0:
                chance = random.random()
                if chance < 0.1:
                    self.rebirth_opportunity += 1
            
            # 注意：在Web应用中，我们不会在这里打印，而是返回状态信息
            return "修炼成功！"
        else:
            return "修炼太过频繁，请稍后再试。"   


    def find_opportunity(self):
        current_time = time.time()
        if current_time - self.last_action_time >= 1:
            self.last_action_time = current_time
            chance = random.random()
            if chance < 0.9:
                # 机缘：灵力增加或减少
                change_factor = random.uniform(1, 2) if random.random() < 0.5 else random.uniform(-0.5, -0.1)
                self.spirit_power += int(self.spirit_power * change_factor)
                message = f"遇到{'奇缘' if change_factor > 0 else '不测'}！功力{'大增！' if change_factor > 0 else '大减！'}"
            else:
                # 提升修炼天赋或战斗天赋
                talent_increase = 1000
                self.cultivation_talent = min(self.cultivation_talent + talent_increase, 10000)
                self.combat_talent = min(self.combat_talent + talent_increase, 10000)
                message = "修炼天赋和战斗天赋增加了！"
            self.update_realm()
            db.session.commit()
            return message
        else:
            return "活动太过频繁，请稍后再试。"

    def duel(self, opponent):
        current_time = time.time()
        if current_time - self.last_action_time >= 1:
            # 你的原始逻辑代码
            self_power = self.spirit_power * self.combat_talent
            opponent_power = opponent.spirit_power * opponent.combat_talent
            
            # 检查战斗力是否有100倍的差距
            duel_result = ""
            if self_power < opponent_power / 100 or opponent_power < self_power / 100:
                # 特殊情况的处理
                if self_power > opponent_power and self_power >= opponent_power * 100:
                    event_chance = random.random()
                    if event_chance < 0.9:
                        opponent.spirit_power = 0
                        opponent.cultivation_talent = min(opponent.cultivation_talent + 1000, 10000)
                        opponent.combat_talent = min(opponent.combat_talent + 1000, 10000)
                        duel_result = f"{opponent.name}的功力全废，需要从头修炼。"
                    else:
                        loss = int(opponent.spirit_power * 0.2)
                        opponent.spirit_power -= loss
                        duel_result = f"{opponent.name}一败涂地，灵力大减。"
                    opponent.update_realm()
                elif opponent_power > self_power and opponent_power >= self_power * 100:
                    event_chance = random.random()
                    if event_chance < 0.9:
                        self.spirit_power = 0
                        self.cultivation_talent = min(self.cultivation_talent + 1000, 10000)
                        self.combat_talent = min(self.combat_talent + 1000, 10000)
                        duel_result = f"{self.name}的功力全废，需要从头修炼。"
                    else:
                        loss = int(self.spirit_power * 0.2)
                        self.spirit_power -= loss
                        duel_result = f"{self.name}一败涂地，灵力大减。"
                    self.update_realm()
            else:
                # 正常情况下的决斗
                if self_power > opponent_power:
                    winner, loser = self, opponent
                else:
                    winner, loser = opponent, self
                winner.spirit_power = int(winner.spirit_power * 1.1)  # 胜者灵力增加10%
                loser.spirit_power = int(loser.spirit_power * 0.9)   # 败者灵力减少10%
                duel_result = f"{winner.name}获胜，灵力增加了10%。{loser.name}失败，灵力减少了10%。"
                winner.update_realm()
                loser.update_realm()

            self.last_action_time = current_time
            opponent.last_action_time = current_time
            db.session.commit()

            return duel_result
        else:
            return f"{self.name}修炼太过频繁，请稍后再试。"
        
    def rebirth(self):
        if self.rebirth_opportunity > 0:
            self.spirit_power = 0  # 重置灵力
            self.rebirth_opportunity -= 1  # 使用一个重生机会
            # 增加修炼天赋和战斗天赋，但不超过 10000
            self.cultivation_talent = min(self.cultivation_talent + 1000, 10000)
            self.combat_talent = min(self.combat_talent + 1000, 10000)
            self.update_realm()  # 更新境界
            db.session.commit()
            return "你进行了重生，修炼天赋和战斗天赋可能增加了。"
        else:
            return "没有重生机会。"



    @staticmethod
    def generate_talent():
        rand_num = random.random()
        if rand_num < 0.9:
            return random.randint(1, 1000)
        elif rand_num < 0.99:
            return random.randint(1001, 10000)
        elif rand_num < 0.999:
            return random.randint(10001, 100000)
        elif rand_num < 0.9999:
            return random.randint(100001, 10000000)
        else:
            return random.randint(10000001, 100000000)

    def update_realm(self):
        realms = ["开元", "弈恒", "玄阳", "正罡", "无绝", "罗法", "天湮", "长帝", "灵神", "封圣", "化梦", "歌殇", "影曜", "奥玄"]
        power = 2
        realm_index = 0
        stage = 0  
        
        while self.spirit_power >= power:
            power *= 2
            stage += 1
            if stage > 2:
                realm_index += 1
                stage = 0

        if realm_index >= len(realms):
            self.realm = "王境"
        elif realm_index < len(realms):
            self.realm = f"{realms[realm_index]}{'前期' if stage == 0 else '中期' if stage == 1 else '后期'}"
        pass
