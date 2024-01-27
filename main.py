import pygame ,random , sys

pygame.init()


WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

display_surface = pygame.display.set_mode((WINDOW_WIDTH , WINDOW_HEIGHT))
pygame.display.set_caption("Space Invaders")

FPS = 60
clock = pygame.time.Clock()



# Define classes
class Game():
    """A class to control gameplay"""
    def __init__(self , player , alien_group , player_bullet_group , alien_bullet_group):
        self.round_number = 1
        self.score = 0

        self.player = player
        self.alien_group = alien_group
        self.player_bullet_group = player_bullet_group
        self.alien_bullet_group = alien_bullet_group

        self.new_round_sound = pygame.mixer.Sound("new_round.wav")
        self.new_round_sound.set_volume(0.2)
        self.breach_sound = pygame.mixer.Sound("breach.wav")
        self.breach_sound.set_volume(0.2)
        self.alien_hit_sound = pygame.mixer.Sound("alien_hit.wav")
        self.alien_hit_sound.set_volume(0.2)
        self.player_hit_sound = pygame.mixer.Sound("alien_hit.wav")
        self.player_hit_sound.set_volume(0.2)

        self.font = pygame.font.Font("Facon.ttf" , 24)

    def update(self):
        
        self.alien_shift()
        self.check_collision()
        self.check_round_completion()

    def draw(self):
        
        WHITE = (255,255,255)

        score_text = self.font.render(f"Score: {self.score}" , True , WHITE)
        score_text_rect = score_text.get_rect()
        score_text_rect.centerx = WINDOW_WIDTH // 2
        score_text_rect.top = 10

        round_text = self.font.render(f"Round: {self.round_number}" , True , WHITE)
        round_text_rect = round_text.get_rect()
        round_text_rect.topleft = (20 , 10)

        lives_text = self.font.render(f"Lives: {self.player.lives}" , True , WHITE)
        lives_text_rect = lives_text.get_rect()
        lives_text_rect.topright = (WINDOW_WIDTH - 20 , 10)


        display_surface.blit(score_text , score_text_rect)
        display_surface.blit(round_text , round_text_rect)
        display_surface.blit(lives_text , lives_text_rect)

        pygame.draw.line(display_surface , WHITE , (0 , 50) , (WINDOW_WIDTH , 50) , 4)
        pygame.draw.line(display_surface , WHITE , (0 , WINDOW_HEIGHT - 100) , (WINDOW_WIDTH , WINDOW_HEIGHT - 100) , 4)

    def start_new_round(self):
        
        for i in range(11):
            for j in range(5):
                alien = Alien(64 + i * 64 , 64 + j * 64 , self.round_number , self.alien_bullet_group)
                self.alien_group.add(alien)

        self.new_round_sound.play()
        self.paused_game(f"Space Invaders Round: {self.round_number}" , "Press 'Enter' to begin")



    def check_collision(self):
        
        alien_hit = pygame.sprite.groupcollide(self.player_bullet_group , self.alien_group , True , True)
        player_get_hit = pygame.sprite.spritecollide(self.player , self.alien_bullet_group , True)

        if alien_hit:
            self.alien_hit_sound.play()
            self.score += 100

        if player_get_hit:
             self.player_hit_sound.play()
             self.player.lives -= 1
             self.check_game_status("Get hit by alien" , "Press 'Enter' to continue !")



    def alien_shift(self):
        shift = False
        
        for alien in (self.alien_group.sprites()):
            if alien.rect.left <= 0 or alien.rect.right >= WINDOW_WIDTH:
                shift = True
        
        # Shift alien downward and direction and check for a breach
        if shift:
            breach = False

            for alien in (self.alien_group.sprites()):
                # shift downwards
                alien.rect.y += 10*self.round_number
                
                # reverse direction 
                alien.direction = alien.direction * -1
                alien.rect.x += alien.direction * alien.velocity

                # if an alien breach the ship
                if alien.rect.bottom >= WINDOW_HEIGHT - 100:
                    breach = True
        
            # Aliens breach the line
            if breach:
                self.breach_sound.play()
                self.player.lives -= 1

                self.check_game_status("Aliens breach the line!",  "Press 'Enter' to continue ")

    def paused_game(self , main_text , sub_text):
        
        # Set colors
        WHITE = (255,255,255)
        BLACK = (0,0,0)

        main_text = self.font.render(main_text , True , WHITE)
        main_text_rect = main_text.get_rect()
        main_text_rect.center = (WINDOW_WIDTH // 2 , WINDOW_HEIGHT // 2)

        sub_text = self.font.render(sub_text , True , WHITE)
        sub_text_rect = sub_text.get_rect()
        sub_text_rect.center = (WINDOW_WIDTH // 2 , WINDOW_HEIGHT // 2 + 64)

        display_surface.fill(BLACK)
        display_surface.blit(main_text , main_text_rect)
        display_surface.blit(sub_text , sub_text_rect)

        pygame.display.update()

        is_paused = True
        while is_paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        is_paused = False


    def reset_game(self):
        
        self.paused_game(f"Final Score: {self.score}" , "Press 'Enter' to play again!")

        self.score = 0
        self.round_number = 1
        self.player.lives = 5

        self.alien_bullet_group.empty()
        self.player_bullet_group.empty()
        self.alien_group.empty()

        self.start_new_round()

    def check_game_status(self , main_text , sub_text):
        #Empty the bullet group and reset player and remaining aliens
        self.alien_bullet_group.empty()
        self.player_bullet_group.empty()
        self.player.reset()

        for alien in self.alien_group:
            alien.reset()
        
        if self.player.lives == 0:
            self.reset_game()
        else:
            self.paused_game(main_text , sub_text)


    def check_round_completion(self):

        if len(self.alien_group.sprites()) == 0:
                self.round_number += 1
                self.score += 1000 * self.round_number
                self.alien_group.empty()
                self.alien_bullet_group.empty()
                self.player_bullet_group.empty()
                self.player.reset()
                self.start_new_round()





class Player(pygame.sprite.Sprite):

    def __init__(self , bullet_group):
        super().__init__()
        self.image = pygame.image.load("player_ship.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.bottom = WINDOW_HEIGHT

        self.lives = 5
        self.velocity = 8

        self.bullet_group = bullet_group

        self.shoot_sound = pygame.mixer.Sound("player_fire.wav")
        self.shoot_sound.set_volume(0.2)

    def update(self):
         keys = pygame.key.get_pressed()

         if keys[pygame.K_LEFT] and self.rect.left > 0:
             self.rect.x -= self.velocity
         if keys[pygame.K_RIGHT] and self.rect.right < WINDOW_WIDTH:
             self.rect.x += self.velocity
        

    def fire(self):

        if len(self.bullet_group) < 2:
            self.shoot_sound.play()
            PlayerBullet(self.rect.centerx , self.rect.top , self.bullet_group)

    def reset(self):
        """ Reset position """
        self.rect.centerx = WINDOW_WIDTH // 2






class Alien(pygame.sprite.Sprite):

    def __init__(self , x , y , velocity , bullet_group):
        super().__init__()
        self.image = pygame.image.load("alien.png")
        self.rect = self.image.get_rect()
        self.rect.topleft = (x , y)

        self.starting_x = x
        self.starting_y = y

        self.direction = 1
        self.velocity = velocity
        self.bullet_group = bullet_group

        self.shoot_sound = pygame.mixer.Sound("alien_fire.wav")
        self.shoot_sound.set_volume(0.2)

    def update(self):
        self.rect.x += self.direction * self.velocity

        # Random fire a bullet
        if random.randint(0, 1000) > 999 and len(self.bullet_group) < 3:
            self.shoot_sound.play()
            self.fire()


    def fire(self):
        AlienBullet(self.rect.centerx , self.rect.bottom , self.bullet_group)

    def reset(self):
        self.rect.topleft = (self.starting_x , self.starting_y)
        self.direction = 1






class PlayerBullet(pygame.sprite.Sprite):

    def __init__(self , x , y , bullet_group):
        super().__init__()
        self.image = pygame.image.load("green_laser.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.velocity = 10
        bullet_group.add(self)

    def update(self):
        self.rect.y -= self.velocity

        if self.rect.top < 0:
            self.kill()





class AlienBullet(pygame.sprite.Sprite):

    def __init__(self , x , y , bullet_group):
        super().__init__()
        self.image = pygame.image.load("red_laser.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.velocity = 10

        bullet_group.add(self)

    def update(self):
        self.rect.y += self.velocity

        if self.rect.bottom > WINDOW_HEIGHT:
            self.kill()





my_player_bullet_group = pygame.sprite.Group()
my_alien_bullet_group = pygame.sprite.Group()

my_player_group = pygame.sprite.Group()
my_player = Player(my_player_bullet_group)
my_player_group.add(my_player)

my_alien_group = pygame.sprite.Group()

my_game = Game(my_player , my_alien_group , my_player_bullet_group , my_alien_bullet_group)
my_game.start_new_round()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                my_player.fire()


    display_surface.fill((0,0,0))

    my_player_group.update()
    my_player_group.draw(display_surface)

    my_player_bullet_group.update()
    my_player_bullet_group.draw(display_surface)

    my_alien_bullet_group.update()
    my_alien_bullet_group.draw(display_surface)

    my_alien_group.update()
    my_alien_group.draw(display_surface)

    my_game.update()
    my_game.draw()

    pygame.display.update()
    clock.tick(FPS)


pygame.quit()