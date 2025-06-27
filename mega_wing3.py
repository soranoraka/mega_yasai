import pyxel



class Background:
    NUM_STARS = 100


    def __init__(self, game):
        self.game = game
        self.stars = []


        for i in range(Background.NUM_STARS):
            x = pyxel.rndi(0, pyxel.width - 1)
            y = pyxel.rndi(0, pyxel.height - 1)
            vy = pyxel.rndf(1, 2.5)
            self.stars. append((x, y, vy))


        self.game.background = self


    def update(self):
        for i, (x, y, vy) in enumerate(self.stars):
            y += vy
            if y >= pyxel.height:
                y -= pyxel.height
                self.stars[i] = (x, y, vy)


    def draw(self):
        if self.game.scene != Game.SCENE_TITLE:
            pyxel.blt(0, 0, 1, 0, 0, 120, 160)


        for x, y, speed in self.stars:
            color = 12 if speed > 1.8 else 5
            pyxel.pset(x, y, color)




class Player:
    MOVE_SPEED = 2
    SHOT_INTERVAL = 6


    def __init__(self, game, x, y):
        self.game =game
        self.x = x
        self.y = y
        self.hit_area = (1, 1, 6, 6)
        self.shot_timer = 0


        self.game.player = self


    def add_damage(self):

        Blast(self.game, self.x + 4, self.y + 4)

        pyxel.stop()
        pyxel.play(0, 2)


        self.game.player = None


        self.game.change_scene(self.game.SCENE_GAMEOVER)

    
    def update(self):
        if pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.x -= Player.MOVE_SPEED
        if pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.x += Player.MOVE_SPEED
        if pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            self.y -= Player.MOVE_SPEED
        if pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            self.y += Player.MOVE_SPEED


        self.x = max(self.x, 0)
        self.x = min(self.x, pyxel.width - 8)
        self.y = max(self.y, 0)
        self.y = min(self.y, pyxel.height - 8)



        if self.shot_timer > 0:
            self.shot_timer -= 1

        if pyxel.btn(pyxel.GAMEPAD1_BUTTON_A) and self.shot_timer == 0:

            Bullet(self.game, Bullet.SIDE_PLAYER, self.x, self.y - 3, -90, 5)


            pyxel.play(3, 0)


            self.shot_timer = Player.SHOT_INTERVAL


    def draw(self):
        pyxel.blt(self.x, self.y, 0, 0, 0, 8, 8, 0)



class Enemy:
    KIND_A = 0
    KIND_B = 1
    KIND_C = 2


    def __init__(self, game, kind, level, x, y):
        self.game = game
        self.kind = kind
        self.level = level
        self.x = x
        self.y = y
        self.hit_area = (0, 0, 7, 7)
        self.armor = self.level - 1
        self.life_time = 0
        self.is_damaged = False


        self.game.enemies.append(self)


    def add_damage(self):
        if self.armor > 0:
            self.armor -= 1
            self.is_damaged = True


            pyxel.play(2, 1, resume=True)
            return
        


        Blast(self.game, self.x + 4, self.y + 4)


        pyxel.play(2, 2, resume=True)
        

        if self in self.game.enemies:
            self.game.enemies.remove(self)


        self.game.score += self.level * 10        


    def calc_player_angle(self):
        player = self.game.player
        if player is None:
            return 90
        else:
            return pyxel.atan2(player.y - self.y, player.x - self.x)
        

    def update(self):

        self.life_time += 1


        if self.kind == Enemy.KIND_A:

            self.y += 1.2


            if self.life_time % 50 == 0:
                player_angle = self.calc_player_angle()
                Bullet(self.game, Bullet.SIDE_ENEMY, self.x, self.y, player_angle, 2)


        elif self.kind == Enemy.KIND_B:

            self.y += 1


            if self.life_time // 30 % 2 == 0:
                self.x += 1.2
            else:
                self.x -= 1.2


        elif self.kind == Enemy.KIND_C:

            self.y += 0.8


            if self.life_time % 40 == 0:
                for i in range(4):
                    Bullet(self.game, Bullet.SIDE_ENEMY, self.x, self.y, i * 45+22, 2)



        if self.y >= pyxel.height:
            if self in self.game.enemies:
                self.game.enemies.remove(self)


    def draw(self):
        if self.is_damaged:
            self.is_damaged = False
            for i in range(1, 15):
                pyxel.pal(i, 15)
            pyxel.blt(self.x, self.y, 0, self.kind * 8 + 8, 0, 8, 8, 0)
            pyxel.pal()
        else:
            pyxel.blt(self.x, self.y, 0, self.kind * 8 + 8, 0, 8, 8, 0)

class Bullet:
    SIDE_PLAYER = 0
    SIDE_ENEMY = 1


    def __init__(self, game, side, x, y, angle, speed):
        self.game = game
        self.side = side
        self.x = x
        self.y = y
        self.vx = pyxel.cos(angle) * speed
        self.vy = pyxel.sin(angle) * speed


        if self.side == Bullet.SIDE_PLAYER:
            self.hit_area = (2, 1, 5, 6)
            game.player_bullets.append(self)
        else:
            self.hit_area = (2, 2, 5, 5)
            game.enemy_bullets.append(self)


    def add_damage(self):

        if self.side == Bullet.SIDE_PLAYER:
            if self in self.game.player_bullets:
                self.game.player_bullets.remove(self)
        else:
            if self in self.game.enemy_bullets:
                self.game.enemy_bullets.remove(self)


    def update(self):

        self.x += self.vx
        self.y += self.vy


        if(
            self.x <= -8
            or self.x >=pyxel.width
            or self.y <= -8
            or self.y >= pyxel.height
        ):
            if self.side == Bullet.SIDE_PLAYER:
                self.game.player_bullets.remove(self)
            else:
                self.game.enemy_bullets.remove(self)


    def draw(self):
        src_x = 0 if self.side == Bullet.SIDE_PLAYER else 8
        pyxel.blt(self.x, self.y, 0, src_x, 8, 8, 8, 0)




class Blast:
    START_RADIUS = 1
    END_RADIUS = 8

    def __init__(self, game, x, y):
        self.game = game
        self.x = x
        self.y = y
        self.radius = Blast.START_RADIUS


        game.blasts.append(self)


    def update(self):

        self.radius += 1

        if self.radius > Blast.END_RADIUS:
            self.game.blasts.remove(self)



    def draw(self):
        pyxel.circ(self.x, self.y, self.radius, 7)
        pyxel.circ(self.x, self.y, self.radius, 10)



def check_collision(entity1, entity2):
    entity1_x1 = entity1.x + entity1.hit_area[0]
    entity1_y1 = entity1.y + entity1.hit_area[1]
    entity1_x2 = entity1.x + entity1.hit_area[2]
    entity1_y2 = entity1.y + entity1.hit_area[3]

    entity2_x1 = entity2.x + entity2.hit_area[0]
    entity2_y1 = entity2.y + entity2.hit_area[1]
    entity2_x2 = entity2.x + entity2.hit_area[2]
    entity2_y2 = entity2.y + entity2.hit_area[3]


    if entity1_x1 > entity2_x2:
        return False
        

    if entity1_x2 < entity2_x1:
        return False
        

    if entity1_y1 > entity2_y2:
        return False
        

    if entity1_y2 < entity2_y1:
        return False
        

    return True



class Game:
    SCENE_TITLE = 0
    SCENE_PLAY = 1
    SCENE_GAMEOVER = 2

    def __init__(self):

        pyxel.init(120, 160, title="Mega Wing")


        pyxel.load("mega_wing3.pyxres")


        self.score = 0
        self.scene = None
        self.play_time = 0
        self.level = 0
        self.background = None
        self.player = None
        self.enemies = []
        self.player_bullets = []
        self.enemy_bullets = []
        self.blasts = []
        

        Background(self)


        self.change_scene(Game.SCENE_TITLE)


        pyxel.run(self.update, self.draw)


    def change_scene(self, scene):
        self.scene = scene


        if self.scene == Game.SCENE_TITLE:

            self.player = None

            self.enemies.clear()
            self.player_bullets.clear()
            self.enemy_bullets.clear()


            pyxel.playm(0, loop=True)


        elif self.scene == Game.SCENE_PLAY:


            self.score = 0
            self.play_time = 0
            self.level = 1


            pyxel.playm(1, loop=True)



            Player(self, 56, 140)


        elif self.scene == Game.SCENE_GAMEOVER:

            self.display_timer = 60

            self.player = None


    def update(self):

        self.background.update()
    
        if self.player is not None:
            self.player.update()




        for enemy in self.enemies.copy():
            enemy.update()


            if self.player is not None and check_collision(self.player, enemy):
                self.player.add_damage()


        for bullet in self.player_bullets.copy():
            bullet.update()


            for enemy in self.enemies.copy():
                if check_collision(enemy, bullet):
                    bullet.add_damage()
                    enemy.add_damage()

                    if self.player is not None:
                        self.player.sound_timer = 5


        for bullet in self.enemy_bullets.copy():
            bullet.update()


            if self.player is not None and check_collision(self.player, bullet):
                bullet.add_damage()
                self.player.add_damage()


        for blast in self.blasts.copy():
            blast.update()


        if self.scene == Game.SCENE_TITLE:
            if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
                pyxel.stop()
                self.change_scene(Game.SCENE_PLAY)

        elif self.scene == Game.SCENE_PLAY:
            self.play_time += 1
            self.level = self.play_time // 450 + 1

            spawn_interval = max(60 - self.level * 10, 10)
            if self.play_time % spawn_interval == 0:
                kind = pyxel.rndi(Enemy.KIND_A, Enemy.KIND_C)
                Enemy(self, kind, self.level, pyxel.rndi(0, 112), -8)
            

        elif self.scene == Game.SCENE_GAMEOVER:
            if self.display_timer > 0:
                self.display_timer -= 1
            else:
                self.change_scene(Game.SCENE_TITLE)


    def draw(self):

        pyxel.cls(0)


        self.background.draw()

        if self.player is not None:
            self.player.draw()

        for enemy in self.enemies:
            enemy.draw()

        for bullet in self.player_bullets:
            bullet.draw()






        for bullet in self.enemy_bullets:
            bullet.draw()


        for blast in self.blasts:
            blast.draw()        

        pyxel.text(39, 4, f"SCORE {self.score:5}",7)


        if self.scene == Game.SCENE_TITLE:
            pyxel.blt(0, 18, 2, 0, 0, 120, 120, 15)
            pyxel.text(31, 148, "- PRESS ENTER - ", 6)

        elif self.scene == Game.SCENE_GAMEOVER:
            pyxel.text(43,78, "GAME OVER", 8)



Game()
             