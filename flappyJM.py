import pygame, random, time
from pygame.locals import *

##################################
######## Global variables ########
##################################

SPEED = 20
GRAVITY = 2.5
GAME_SPEED = 15

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600

GROUND_WIDTH = 2 * WINDOW_WIDTH
GROUND_HEIGHT = 100

PIPE_WIDTH = 80
PIPE_HEIGHT = 500
PIPE_GAP = 150

# Initialize mixer
pygame.mixer.init()

# Loading sounds into mixer
WING_SOUND = pygame.mixer.Sound('assets/audio/wing.wav')
HIT_SOUND = pygame.mixer.Sound('assets/audio/hit.wav')
POINT_SOUND = pygame.mixer.Sound('assets/audio/point.wav')

##################################
####### Class Declarations #######
##################################


#********** Bird Class **********

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.images = [
            pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha(),
            pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha(),
            pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha()
        ]

        self.speed = SPEED

        self.current_image = 0
        self.image = self.images[self.current_image]
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = WINDOW_WIDTH / 6
        self.rect[1] = WINDOW_HEIGHT / 2

    def update(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.speed += GRAVITY
        self.rect[1] += self.speed

    def bump(self):
        self.speed = -SPEED

    def begin(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]


#********** Pipe Class **********

class Pipe(pygame.sprite.Sprite):
    def __init__(self, inverted, xpos, ysize):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load('assets/sprites/pipe-jm.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDTH, PIPE_HEIGHT))

        self.rect = self.image.get_rect()
        self.rect[0] = xpos

        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = -(self.rect[3] - ysize)
        else:
            self.rect[1] = WINDOW_HEIGHT - ysize

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect[0] -= GAME_SPEED


#********** Ground Class **********

class Ground(pygame.sprite.Sprite):
    def __init__(self, xpos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprites/base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDTH, GROUND_HEIGHT))

        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = WINDOW_HEIGHT - GROUND_HEIGHT

    def update(self):
        self.rect[0] -= GAME_SPEED


##################################
####### Utility Functions ########
##################################

def is_off_screen(sprite):
    return sprite.rect[0] < -(sprite.rect[2])

def get_random_pipes(xpos):
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, WINDOW_HEIGHT - size - PIPE_GAP)
    return pipe, pipe_inverted

def display_score(screen, score):
    font = pygame.font.Font(None, 36)
    score_surface = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_surface, (10, 10))

def display_final_score(screen, score):
    game_over_surface = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
    screen.blit(game_over_surface, (WINDOW_WIDTH // 2 - game_over_surface.get_width() // 2, 100))

    font = pygame.font.SysFont(None, 48) 
    final_score_surface = font.render(f"Final Score: {score}", True, (255, 255, 255))
    screen.blit(final_score_surface, (WINDOW_WIDTH // 2 - final_score_surface.get_width() // 2, 250))

    play_again_surface = font.render("Press R to Replay", True, (255, 255, 255))
    screen.blit(play_again_surface, (WINDOW_WIDTH // 2 - play_again_surface.get_width() // 2, 300))


##################################
######### Main Function ##########
##################################
if __name__ == "__main__":
    pygame.init()
    try:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Flappy Bird')

        BACKGROUND = pygame.image.load('assets/sprites/background-day2.png')
        BACKGROUND = pygame.transform.scale(BACKGROUND, (WINDOW_WIDTH, WINDOW_HEIGHT))
        BEGIN_IMAGE = pygame.image.load('assets/sprites/message4.png').convert_alpha()

        while True:  # Replay loop
            bird_group = pygame.sprite.Group()
            bird = Bird()
            bird_group.add(bird)

            ground_group = pygame.sprite.Group()

            for i in range(2):
                ground = Ground(GROUND_WIDTH * i)
                ground_group.add(ground)

            pipe_group = pygame.sprite.Group()
            for i in range(2):
                pipes = get_random_pipes(WINDOW_WIDTH * i + 800)
                pipe_group.add(pipes[0])
                pipe_group.add(pipes[1])

            clock = pygame.time.Clock()

            score = 0
            last_pipe_x = 0

            begin = True

            # Initial Game Start Loop
            while begin:
                clock.tick(15)

                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        exit()
                    elif event.type == KEYDOWN:
                        if event.key == K_SPACE or event.key == K_UP:
                            bird.bump()
                            WING_SOUND.play()
                            begin = False

                screen.blit(BACKGROUND, (0, 0))
                screen.blit(BEGIN_IMAGE, (120, 150))

                if is_off_screen(ground_group.sprites()[0]):
                    ground_group.remove(ground_group.sprites()[0])

                    new_ground = Ground(GROUND_WIDTH - 20)
                    ground_group.add(new_ground)

                bird.begin()
                ground_group.update()

                bird_group.draw(screen)
                ground_group.draw(screen)

                pygame.display.update()

            ## Main Game Loop ##
            while True:
                clock.tick(15)

                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        exit()
                    elif event.type == KEYDOWN:
                        if event.key == K_SPACE or event.key == K_UP:
                            bird.bump()
                            WING_SOUND.play()

                screen.blit(BACKGROUND, (0, 0))

                if is_off_screen(ground_group.sprites()[0]):
                    ground_group.remove(ground_group.sprites()[0])

                    new_ground = Ground(GROUND_WIDTH - 20)
                    ground_group.add(new_ground)

                if is_off_screen(pipe_group.sprites()[0]):
                    pipe_group.remove(pipe_group.sprites()[0])
                    pipe_group.remove(pipe_group.sprites()[0])

                    pipes = get_random_pipes(WINDOW_WIDTH * 2)

                    pipe_group.add(pipes[0])
                    pipe_group.add(pipes[1])

                ## SCORE
                # Check if bird passed a pipe pair
                for pipe in pipe_group:
                    # Only count the bottom pipe for scoring
                    if pipe.rect.right < bird.rect.left and not hasattr(pipe, 'scored') and pipe.rect.y > 0:
                        score += 1
                        pipe.scored = True  # Mark this pipe pair as scored
                        POINT_SOUND.play()  # Play the point sound

                bird_group.update()
                ground_group.update()
                pipe_group.update()

                bird_group.draw(screen)
                pipe_group.draw(screen)
                ground_group.draw(screen)

                display_score(screen, score)

                pygame.display.update()

                if (
                    pygame.sprite.groupcollide(
                        bird_group, ground_group, False, False, pygame.sprite.collide_mask
                    )
                    or pygame.sprite.groupcollide(
                        bird_group, pipe_group, False, False, pygame.sprite.collide_mask
                    )
                ):
                    HIT_SOUND.play()
                    time.sleep(1)
                    break

            # Display final score and replay option
            screen.fill((0, 0, 0))
            display_final_score(screen, score)
            pygame.display.update()

            replay = False
            while not replay:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        exit()
                    elif event.type == KEYDOWN and event.key == K_r:
                        replay = True

    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        pygame.quit()
        exit()
