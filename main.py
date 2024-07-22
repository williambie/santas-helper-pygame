import pygame
import random
import math

# Initialization
pygame.init()
pygame.font.init()

# Game window settings and assets
display_width = 1200
display_height = 800
screen = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Santas Helper!')
clock = pygame.time.Clock()

# Constants
FONT_X = 550
FONT_Y = 100
SCROLL_SPEED_INITIAL = 2
TOP_BOUNDARY = (display_height // 2) - 40
TOP_BOUNDARY_ICEHOLES = (display_height // 2) + 80
PLAYER_START_POS = (100, (display_height - 133) / 2 + 300)

# Global variables
total_lives = 3
player_score = 0
high_score = 0

# Load and play music
pygame.mixer.init()
giftSound = pygame.mixer.Sound("sounds/giftsound.mp3")
iceSound = pygame.mixer.Sound("sounds/iceSound.mp3")
jumpSound = pygame.mixer.Sound("sounds/jumpSound.wav")
pygame.mixer.music.load("sounds/soundtrack.mp3")
pygame.mixer.music.play(-1)

# Font for rendering text
font = pygame.font.Font(None, 50)

# Load assets
def load_assets():
    player_img = pygame.transform.scale(pygame.image.load("images/player.png").convert_alpha(), (89, 133))
    background_img = pygame.transform.scale(pygame.image.load("images/background.png").convert_alpha(), (int(display_width), int(display_height)))
    gift_img = pygame.transform.scale(pygame.image.load("images/gift.png").convert_alpha(), (50, 50))
    ice_img = pygame.transform.scale(pygame.image.load("images/icehole.png").convert_alpha(), (122, 56))
    heart_img = pygame.transform.scale(pygame.image.load("images/heart.png").convert_alpha(), (50, 50))
    trophy_img = pygame.transform.scale(pygame.image.load("images/trophy.png").convert_alpha(), (50,50))

    return player_img, background_img, gift_img, ice_img, heart_img, trophy_img

# Score handling
def save_score(score, filename="score.txt"):
    with open(filename, "w") as f:
        f.write(str(score))

def load_score(filename="score.txt"):
    try:
        with open(filename, "r") as f:
            return int(f.readline())
    except (FileNotFoundError, ValueError):
        return 0 

# Player class
class Player():
    def __init__(self, image, pos):
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.speed = 500
        self.backwardsspeed = 800
        self.isJump = False
        self.jumpStart = 10
        self.jumpPeak = -10
        self.jumpSpeed = 0.2
        self.jumpHeightMultiplier = 0.10
        self.invulnerability_timer = 2
        hitbox_height = self.rect.height * 0.6
        hitbox_top = self.rect.bottom - hitbox_height
        self.hitbox = pygame.Rect(self.rect.left, hitbox_top, self.rect.width, hitbox_height)

    def move(self, left=False, right=False, up=False, down=False, delta_time=0):
        self.hitbox.x = self.rect.x
        self.hitbox.bottom = self.rect.bottom 
        if left:
            self.rect.x -= self.backwardsspeed * delta_time
        if right:
            self.rect.x += self.speed * delta_time

        if self.isJump:
            if self.jumpStart >= self.jumpPeak:
                jumpDirection = 1 if self.jumpStart > 0 else -1
                self.rect.y -= (self.jumpStart ** 2) * self.jumpHeightMultiplier * jumpDirection
                self.jumpStart -= self.jumpSpeed
            else:
                self.isJump = False
                self.jumpStart = 10
                self.rect.y = max(TOP_BOUNDARY, self.rect.y)
        elif up:
            self.rect.y = max(TOP_BOUNDARY, self.rect.y - self.speed * delta_time)
        elif down:
            self.rect.y += self.speed * delta_time

        if self.invulnerability_timer > 0:
            self.invulnerability_timer -= delta_time

        # Boundaries for moving 
        self.rect.x = max(0, min(display_width - self.rect.width, self.rect.x))
        self.rect.y = min(self.rect.y, display_height - self.rect.height)

    def render(self, surface):
        surface.blit(self.image, self.rect.topleft)

    def display_info(self, score, high_score, lives, heart_img, gift_img, font, surface):
        score_img = font.render(f"{score}", True, (0, 0, 0))
        high_score_img = font.render(f"{high_score}", True, (0, 0, 0))

        gift_img_x = FONT_X + score_img.get_width()
        gift_img_y = FONT_Y
        trophy_img_x = FONT_X + score_img.get_width()
        trophy_img_y = FONT_Y

        surface.blit(gift_img, (gift_img_x, gift_img_y))
        surface.blit(score_img, (FONT_X + 90, FONT_Y + 10))
        surface.blit(trophy_img, (trophy_img_x, trophy_img_y + 70))
        surface.blit(high_score_img, (FONT_X + 90, FONT_Y + 75))

        heart_x = FONT_X
        heart_y = FONT_Y - 70
        for i in range(lives):
            surface.blit(heart_img, (heart_x + (i * 60), heart_y))

# Background class
class Background():
    def __init__(self, image, width):
        self.image = image
        self.width = width
        self.scroll = 0

    def update(self):
        self.scroll -= 2
        if abs(self.scroll) > self.width:
            self.scroll = 0

    def render(self, surface):
        tiles = math.ceil(display_width / self.width) + 1
        for i in range(tiles):
            surface.blit(self.image, (i * self.width + self.scroll, 0))

# Gift and IceHole classes
class Gift():
    def __init__(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.spawn()

    def spawn(self):
        self.rect.x = display_width + random.randint(0, 300)
        self.rect.y = random.randint(TOP_BOUNDARY, display_height - self.rect.height)

    def update(self, scroll_speed):
        self.rect.x -= scroll_speed

    def render(self, surface):
        surface.blit(self.image, self.rect.topleft)

class IceHole:
    def __init__(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.hitbox_inset = 20
        self.hitbox = pygame.Rect(self.rect.left + self.hitbox_inset, 
                                  self.rect.top + self.hitbox_inset, 
                                  self.rect.width - 2 * self.hitbox_inset, 
                                  self.rect.height - 2 * self.hitbox_inset)
        self.spawn()

    def spawn(self):
        self.rect.x = display_width + random.randint(0, 300)
        self.rect.y = random.randint(TOP_BOUNDARY_ICEHOLES, display_height - self.rect.height)
        self.hitbox.topleft = (self.rect.left + self.hitbox_inset, 
                               self.rect.top + self.hitbox_inset)

    def update(self, scroll_speed):
        self.rect.x -= scroll_speed
        self.hitbox.x = self.rect.x + self.hitbox_inset
        self.hitbox.y = self.rect.y + self.hitbox_inset

    def render(self, surface):
        surface.blit(self.image, self.rect.topleft)

# Main game logic
def run_game():
    global player_score, high_score, total_lives

    player = Player(player_img, PLAYER_START_POS)
    background = Background(background_img, background_img.get_width())

    gifts = []
    ice_holes = []
    gift_spawn_timer = 0
    ice_spawn_timer = 0
    scroll_speed = SCROLL_SPEED_INITIAL
    current_multiple = set()

    running = True
    while running:
        delta_time = clock.tick(144) / 1000

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_score(high_score)
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not player.isJump:
                    jumpSound.play()
                    player.isJump = True

        # Player movement
        keys = pygame.key.get_pressed()
        player.move(
            left=keys[pygame.K_a],
            right=keys[pygame.K_d],
            up=keys[pygame.K_w],
            down=keys[pygame.K_s],
            delta_time=delta_time
        )

        # Spawning and updating gifts
        gift_spawn_timer += delta_time
        if gift_spawn_timer >= random.randint(2, 5):
            gifts.append(Gift(gift_img))
            gift_spawn_timer = 0

        # Spawning and updating ice holes
        ice_spawn_timer += delta_time
        if ice_spawn_timer >= random.randint(2, 7):
            ice_holes.append(IceHole(ice_img))
            ice_spawn_timer = 0

        # Update speed based on score
        current_increase = player_score // 10
        if current_increase and current_increase not in current_multiple:
            scroll_speed += 1
            current_multiple.add(current_increase)

        # Update and collision detection
        for gift in gifts[:]:
            gift.update(scroll_speed)
            if player.hitbox.colliderect(gift.rect):
                player_score += 1
                giftSound.play()
                gifts.remove(gift)
                high_score = max(high_score, player_score)

        for icehole in ice_holes[:]:
            icehole.update(scroll_speed)
            if player.hitbox.colliderect(icehole.hitbox) and player.invulnerability_timer <= 0 and player.isJump == False:
                total_lives -= 1
                player.invulnerability_timer = 2
                iceSound.play()
                if total_lives == 0:
                    save_score(high_score)
                    running = False

        # Update background
        background.update()

        # Clear screen and render everything
        screen.fill((0, 0, 0))
        background.render(screen)
        for icehole in ice_holes:
            icehole.render(screen)
        for gift in gifts:
            gift.render(screen)
        player.render(screen)
        player.display_info(player_score, high_score, total_lives, heart_img, gift_img, font, screen)

        pygame.display.flip()

    # End of game cleanup
    save_score(high_score)
    pygame.quit()


# Main execution
if __name__ == "__main__":
    player_img, background_img, gift_img, ice_img, heart_img, trophy_img = load_assets()
    high_score = load_score()
    run_game()
    pygame.quit()
