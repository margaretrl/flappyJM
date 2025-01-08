import pygame, random, time 
from pygame.locals import *

##################################
######## Global variables ########
##################################

SPEED = 20  # Initial speed for the bird
GRAVITY = 2.5  # How fast the bird falls
GAME_SPEED = 15  # Speed at which pipes and ground move

# Window and ground dimensions
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
GROUND_WIDTH = 2 * WINDOW_WIDTH
GROUND_HEIGHT = 100

# Pipe dimensions and gap
PIPE_WIDTH = 80
PIPE_HEIGHT = 500
PIPE_GAP = 150

# Initialize the sound mixer for audio effects
pygame.mixer.init()

# Load sound effects
WING_SOUND = pygame.mixer.Sound('assets/audio/wing.wav')  # Flapping sound
HIT_SOUND = pygame.mixer.Sound('assets/audio/hit.wav')  # Collision sound
POINT_SOUND = pygame.mixer.Sound('assets/audio/point.wav')  # Scoring sound

##################################
####### Class Declarations #######
##################################

#********** Bird Class **********

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Load three bird images for flapping animation
        self.images = [
            pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha(),
            pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha(),
            pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha()
        ]

        self.speed = SPEED  # Initial upward speed

        self.current_image = 0  # Index to cycle through images for animation
        self.image = self.images[self.current_image]  # Start with the first image
        self.mask = pygame.mask.from_surface(self.image)  # For collision detection

        # Position the bird
        self.rect = self.image.get_rect()
        self.rect[0] = WINDOW_WIDTH / 6  # X position
        self.rect[1] = WINDOW_HEIGHT / 2  # Y position

    def update(self):
        # Animate the bird by cycling through images
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]

        # Gravity affects the bird's speed
        self.speed += GRAVITY
        self.rect[1] += self.speed  # Move the bird downward

        # Add upper limit: prevent bird from flying off the top
        if self.rect[1] < 0:
            self.rect[1] = 0  # Reset bird's position to the top boundary

    def bump(self):
        # Make the bird "jump" upward
        self.speed = -SPEED

    def begin(self):
        # Animation for the start screen
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]


#********** Pipe Class **********

class Pipe(pygame.sprite.Sprite):
    def __init__(self, inverted, xpos, ysize):
        super().__init__()

        # Load and resize the pipe image
        self.image = pygame.image.load('assets/sprites/pipe-jm.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDTH, PIPE_HEIGHT))

        self.rect = self.image.get_rect()
        self.rect[0] = xpos  # X position of the pipe

        # Position the pipe based on whether it is inverted (top pipe)
        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = -(self.rect[3] - ysize)
        else:
            self.rect[1] = WINDOW_HEIGHT - ysize  # Bottom pipe position

        self.mask = pygame.mask.from_surface(self.image)  # For collision detection

    def update(self):
        # Move the pipe leftward
        self.rect[0] -= GAME_SPEED


#********** Ground Class **********

class Ground(pygame.sprite.Sprite):
    def __init__(self, xpos):
        super().__init__()
        self.image = pygame.image.load('assets/sprites/base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDTH, GROUND_HEIGHT))

        self.mask = pygame.mask.from_surface(self.image)  # For collision detection

        self.rect = self.image.get_rect()
        self.rect[0] = xpos  # X position
        self.rect[1] = WINDOW_HEIGHT - GROUND_HEIGHT  # Y position at the bottom

    def update(self):
        # Move the ground leftward
        self.rect[0] -= GAME_SPEED


##################################
####### Utility Functions ########
##################################

def is_off_screen(sprite):
    # Check if a sprite has moved completely off-screen
    return sprite.rect[0] < -(sprite.rect[2])

def get_random_pipes(xpos):
    # Generate a pair of pipes with a random gap
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)  # Bottom pipe
    pipe_inverted = Pipe(True, xpos, WINDOW_HEIGHT - size - PIPE_GAP)  # Top pipe
    return pipe, pipe_inverted

def display_score(screen, score):
    # Display the current score on the top-left corner
    font = pygame.font.Font(None, 36)
    score_surface = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_surface, (10, 10))

def display_final_score(screen, score):
    # Display the final score and "play again" message
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
    pygame.init()  # Initialize pygame
    try:
        # Set up the game screen
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Flappy JM')

        # Load background and start screen images
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

                # Blit stands for Block Image Transfer
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

                        # Gradually increase game speed
                        if score % 5 == 0:  # Increase speed every 5 points
                            GAME_SPEED += 1.3

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
                        GAME_SPEED = 15

    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        pygame.quit()
        exit()
