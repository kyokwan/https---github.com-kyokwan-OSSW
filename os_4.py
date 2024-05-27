import pygame
import sys
import Map_1

pygame.init()

# 화면 크기 설정
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("점프 점프")

# 색깔
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
FLOOR_COLOR = (144, 228, 144)  # 바닥 색
SPIKE_COLOR = (0, 0, 0)        # 가시 색

# 캐릭터 속성
character_width, character_height = 20, 20
character_x, character_y = 30, SCREEN_HEIGHT - character_height * 2
character_speed = 6
jump_speed = 20
gravity = 1.4

# 바닥 속성
floor_height = 40
floor_y = SCREEN_HEIGHT - floor_height

# 발판 속성
platform_width, platform_height = 50, 20
platform_color = BLUE

# 가시 속성 및 위치
spike_width, spike_height = 10, 20
spike_positions = [(x, floor_y - spike_height) for x in range(550, 600, spike_width)]

# 맵의 최대 크기
max_map_width = 1200  

# 바닥 구멍 정보 로드
floor_holes = Map_1.floor_holes

# 점프 블록
class Block:
    def __init__(self, x, y, speed=0, cloud=False):
        self.x = x
        self.y = y
        self.speed = speed
        self.cloud = cloud  # 구름 블록 여부
        self.is_visible = True

    def move(self):
        if self.speed != 0:
            self.x += self.speed
            if self.x > SCREEN_WIDTH:
                self.is_visible = False

# 맵 로드
def load_map(map_module):
    blocks = [Block(x, y, cloud=(y == 260 and x in [100])) for x, y in map_module.blocks_positions]
    return blocks

# 초기 맵 설정
map_modules = [Map_1]
current_map_index = 0
blocks = load_map(map_modules[current_map_index])

# 충돌 영역 설정
del_block_1 = pygame.Rect(220, 350, 100, 100)
add_block_1 = pygame.Rect(50, 340, 30, 30)
trigger_moving_block_zone = pygame.Rect(160, 220, 30, 30)
clock = pygame.time.Clock()

# 폰트 설정
font = pygame.font.Font(None, 20)

# 타이머 설정
block_spawn_time = 0
block_spawn_delay = 2  # 2초 후 블록 생성

def check_collision(character, blocks):
    for block in blocks:
        if block.is_visible and not block.cloud and character.colliderect(pygame.Rect(block.x, block.y, platform_width, platform_height)):
            return block
    return None

def check_bottom_collision(character, block):
    if block.cloud:  # 구름 블록일 경우
        if character.bottom >= block.y and character.top < block.y and character.right > block.x and character.left < block.x + platform_width:
            return True
    else:
        block_rect = pygame.Rect(block.x, block.y, platform_width, platform_height)
        if character.bottom >= block_rect.top and character.top < block_rect.top and character.right > block_rect.left and character.left < block_rect.right:
            return True
    return False

# 가시 충돌 감지
def check_spike_collision(character, spikes):
    for spike in spikes:
        if character.colliderect(pygame.Rect(spike[0], spike[1], spike_width, spike_height)):
            return True
    return False

# 특정 영역 충돌 감지
def check_trigger_zone_collision(character, trigger_zone):
    return character.colliderect(trigger_zone)

# 다음 맵 로드
def load_next_map():
    global current_map_index, character_x, character_y, blocks, camera_x
    current_map_index += 1
    if current_map_index < len(map_modules):
        character_x, character_y = 30, SCREEN_HEIGHT - character_height * 2
        camera_x = 0
        blocks = load_map(map_modules[current_map_index])
    else:
        print("게임 클리어!")
        pygame.quit()
        sys.exit()

# 바닥 속성을 변경할 변수 추가
floor_dropped = False
drop_y = SCREEN_HEIGHT - floor_height + 200  # 떨어진 바닥의 y 좌표

# 게임 초기화
def reset_game():
    global character_x, character_y, vertical_momentum, is_on_ground, blocks, additional_block_added_1, additional_block_added_2, moving_block_triggered, block_spawn_time, block_spawned, camera_x
    character_x, character_y = 30, SCREEN_HEIGHT - character_height * 2
    vertical_momentum = 0
    is_on_ground = True
    additional_block_added_1 = False  
    additional_block_added_2 = False  
    moving_block_triggered = False  # 움직이는 블록 초기화
    block_spawn_time = 0  # 타이머 초기화
    block_spawned = False  # 블록이 생성되지 않은 상태로 초기화
    camera_x = 0  # 카메라 초기화
    blocks = load_map(map_modules[current_map_index])
    for block in blocks:
        block.is_visible = True

# 게임 루프
running = True
vertical_momentum = 0
is_on_ground = True
space_pressed = False
additional_block_added_1 = False 
additional_block_added_2 = False 
moving_block_triggered = False  # 움직이는 블록이 생성되었는지 여부
block_spawned = False  # 블록이 생성되지 않은 상태로 초기화
camera_x = 0  # 카메라 초기화

# 캐릭터의 상단이 블록의 하단에 닿을 때
def check_top_collision(character, block):
    block_rect = pygame.Rect(block.x, block.y, platform_width, platform_height)
    if (character.top <= block_rect.bottom and character.bottom > block_rect.bottom and
            character.right > block_rect.left and character.left < block_rect.right):
        return True
    return False

# 게임 루프 내 충돌 검사 및 처리 부분 수정
while running:
    screen.fill(WHITE)
    character_rect = pygame.Rect(character_x, character_y, character_width, character_height)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                space_pressed = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                space_pressed = False

    if space_pressed and is_on_ground:
        vertical_momentum = -jump_speed
        is_on_ground = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        character_x -= character_speed
    if keys[pygame.K_RIGHT]:
        character_x += character_speed

    # 화면 범위 제한, 바닥 충돌 처리
    character_x = max(0, character_x)  # 캐릭터가 왼쪽으로 화면을 벗어나지 못하게 제한
    character_x = min(character_x, max_map_width - character_width)  # 캐릭터가 오른쪽으로 맵의 끝을 벗어나지 못하게 제한

    vertical_momentum += gravity
    character_y += vertical_momentum

    # y가 600을 넘으면 게임 리셋
    if character_y > SCREEN_HEIGHT:
        reset_game()

    # 바닥과의 충돌 체크
    is_on_ground = False
    if character_y >= floor_y - character_height:
        is_in_hole = False
        for hole_start, hole_end in floor_holes:
            if hole_start < character_x < hole_end:
                is_in_hole = True
                break
        
        if not is_in_hole:
            character_y = floor_y - character_height
            vertical_momentum = 0
            is_on_ground = True

    # 화면 중앙으로 카메라 위치 조정 (오른쪽으로 갈 때만)
    if character_x > SCREEN_WIDTH // 2:
        camera_x = character_x - SCREEN_WIDTH // 2
        camera_x = min(camera_x, max_map_width - SCREEN_WIDTH)
    else:
        camera_x = 0

    # 바닥 그리기
    pygame.draw.rect(screen, FLOOR_COLOR, (0 - camera_x, floor_y, SCREEN_WIDTH, floor_height))
    for hole_start, hole_end in floor_holes:
        pygame.draw.rect(screen, WHITE, (hole_start - camera_x, floor_y, hole_end - hole_start, floor_height))

    # 충돌 검사 및 처리
    block_collided = check_collision(character_rect, blocks)
    if block_collided:
        if vertical_momentum > 0:
            character_y = block_collided.y - character_height
            vertical_momentum = 0
            is_on_ground = True
        elif check_top_collision(character_rect, block_collided):
            character_y = block_collided.y + platform_height
            vertical_momentum = gravity  # 반대 방향으로 튕겨나기
            is_on_ground = False

    # 가시 충돌 검사
    if check_spike_collision(character_rect, spike_positions):
        reset_game()

    # 특정 영역 충돌 검사 및 처리
    if check_trigger_zone_collision(character_rect, del_block_1):
        blocks[1].is_visible = False
        
    # 움직이는 블록 생성 트리거
    if check_trigger_zone_collision(character_rect, trigger_moving_block_zone) and not moving_block_triggered and not block_spawned:
        block_spawn_time = pygame.time.get_ticks()  # 현재 시간 저장
        moving_block_triggered = True

    if moving_block_triggered and not block_spawned and (pygame.time.get_ticks() - block_spawn_time) >= block_spawn_delay * 400:
        moving_block = Block(-platform_width, 230, speed=9)  # 왼쪽에서 오른쪽으로 이동하는 블록
        blocks.append(moving_block)
        block_spawned = True  # 블록이 생성되었음을 표시

    # 추가 블록 영역 충돌 검사
    if character_rect.colliderect(add_block_1) and not additional_block_added_1:
        blocks.append(Block(50, 375))
        additional_block_added_1 = True

    # 블록 이동 및 충돌 검사
    for block in blocks:
        if block.speed != 0:
            block.move()
            if block.is_visible and character_rect.colliderect(pygame.Rect(block.x, block.y, platform_width, platform_height)):
                reset_game()

    # 발판
    for block in blocks:
        if block.is_visible:
            pygame.draw.rect(screen, platform_color, (block.x - camera_x, block.y, platform_width, platform_height))
            # 발판 위치 좌표
            text = font.render(f"({block.x}, {block.y})", True, RED)
            screen.blit(text, (block.x - camera_x, block.y - 20))

    # 가시 그리기
    for spike in spike_positions:
        pygame.draw.rect(screen, SPIKE_COLOR, (spike[0] - camera_x, spike[1], spike_width, spike_height))

    # 충돌 영역 그리기 (디버깅용)
    pygame.draw.rect(screen, (0, 0, 0), del_block_1.move(-camera_x, 0), 2)
    pygame.draw.rect(screen, (0, 255, 0), add_block_1.move(-camera_x, 0), 2)
    pygame.draw.rect(screen, (0, 0, 255), trigger_moving_block_zone.move(-camera_x, 0), 2)

    # 캐릭터
    pygame.draw.rect(screen, RED, character_rect.move(-camera_x, 0))
    pygame.display.update()
    clock.tick(60)  # 프레임 속도 유지

pygame.quit()
sys.exit()
