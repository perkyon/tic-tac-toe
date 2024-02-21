import pygame
import sys
import random
import copy

# Инициализация Pygame
pygame.init()

# Константы
COLUMNS = 7
ROWS = 6
WIDTH = 700
HEIGHT = 600
CELL_SIZE = WIDTH // COLUMNS
LINE_WIDTH = 4
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
X_COLOR = (84, 84, 84)
O_COLOR = (255, 255, 255)
FONT = pygame.font.Font(None, 36)

# Настройка дисплея
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Крестики-нолики на торе с гравитацией')

player_symbol = None
bot_symbol = None
board = [[' ' for _ in range(COLUMNS)] for _ in range(ROWS)]

# Функции для работы с текстом и кнопками
def text_objects(text, font):
    textSurface = font.render(text, True, (0, 0, 0))
    return textSurface, textSurface.get_rect()

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def draw_button(msg, x, y, w, h, ic, ac, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(screen, ac, (x, y, w, h))
        if click[0] == 1 and action is not None:
            action()         
    else:
        pygame.draw.rect(screen, ic, (x, y, w, h))

    smallText = pygame.font.Font(None, 20)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ((x+(w/2)), (y+(h/2)))
    screen.blit(textSurf, textRect)

# Функции для работы с игровым процессом
def apply_gravity(board, col, turn):
    for row in range(ROWS-1, -1, -1):
        if board[row][col] == ' ':
            board[row][col] = turn
            return True
    return False

def check_win(board, player):
    for row in range(ROWS):
        for col in range(COLUMNS):
            # Проверки для горизонтали, вертикали и диагоналей
            if col <= COLUMNS - 4 and all(board[row][(col + i) % COLUMNS] == player for i in range(4)):
                return True
            if row <= ROWS - 4 and all(board[(row + i) % ROWS][col] == player for i in range(4)):
                return True
            if row <= ROWS - 4 and col <= COLUMNS - 4 and all(board[(row + i) % ROWS][(col + i) % COLUMNS] == player for i in range(4)):
                return True
            if row >= 3 and col <= COLUMNS - 4 and all(board[(row - i) % ROWS][(col + i) % COLUMNS] == player for i in range(4)):
                return True
    return False

def draw_X(x, y):
    pygame.draw.line(screen, X_COLOR, (x + CELL_SIZE * 0.2, y + CELL_SIZE * 0.2), (x + CELL_SIZE * 0.8, y + CELL_SIZE * 0.8), LINE_WIDTH)
    pygame.draw.line(screen, X_COLOR, (x + CELL_SIZE * 0.8, y + CELL_SIZE * 0.2), (x + CELL_SIZE * 0.2, y + CELL_SIZE * 0.8), LINE_WIDTH)

def draw_O(x, y):
    pygame.draw.circle(screen, O_COLOR, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), int(CELL_SIZE * 0.3), LINE_WIDTH)

def draw_board(board):
    screen.fill(BG_COLOR)
    for row in range(ROWS):
        for col in range(COLUMNS):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, LINE_COLOR, rect, LINE_WIDTH)
            if board[row][col] == 'X':
                draw_X(col * CELL_SIZE, row * CELL_SIZE)
            elif board[row][col] == 'O':
                draw_O(col * CELL_SIZE, row * CELL_SIZE)

# Функции для выбора символа игрока
def choose_symbol_screen():
    global player_symbol, bot_symbol
    intro = True
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
        screen.fill(BG_COLOR)
        draw_text('Выберите символ', FONT, (255, 255, 255), screen, WIDTH / 2, HEIGHT / 2 - 100)
        
        draw_button('X', 150, HEIGHT / 2, 100, 50, X_COLOR, (200,0,0), choose_X)
        draw_button('O', 450, HEIGHT / 2, 100, 50, O_COLOR, (0,200,0), choose_O)
        
        pygame.display.update()

def choose_X():
    global player_symbol, bot_symbol
    player_symbol = 'X'
    bot_symbol = 'O'
    main()

def choose_O():
    global player_symbol, bot_symbol
    player_symbol = 'O'
    bot_symbol = 'X'
    main()

# Оценочная функция
def evaluate_board(board, symbol):
    opponent_symbol = 'O' if symbol == 'X' else 'X'
    score = 0
    if check_win(board, symbol):
        score += 100
    elif check_win(board, opponent_symbol):
        score -= 100
    return score

# Минимакс с альфа-бета отсечением
def minimax(board, depth, alpha, beta, maximizingPlayer, symbol):
    opponent_symbol = 'O' if symbol == 'X' else 'X'
    if depth == 0 or check_win(board, symbol) or check_win(board, opponent_symbol):
        return evaluate_board(board, symbol), None

    if maximizingPlayer:
        maxEval = float('-inf')
        best_col = None
        for col in range(COLUMNS):
            if board[ROWS-1][col] == ' ':
                temp_board = copy.deepcopy(board)
                apply_gravity(temp_board, col, symbol)
                eval, _ = minimax(temp_board, depth-1, alpha, beta, False, symbol)
                if eval > maxEval:
                    maxEval = eval
                    best_col = col
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return maxEval, best_col
    else:
        minEval = float('inf')
        best_col = None
        for col in range(COLUMNS):
            if board[ROWS-1][col] == ' ':
                temp_board = copy.deepcopy(board)
                apply_gravity(temp_board, col, opponent_symbol)
                eval, _ = minimax(temp_board, depth-1, alpha, beta, True, symbol)
                if eval < minEval:
                    minEval = eval
                    best_col = col
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return minEval, best_col
    
def evaluate_almost_winning_positions(board, symbol):
    score = 0
    opponent_symbol = 'O' if symbol == 'X' else 'X'
    
    # Проверяем позиции, где можно выиграть за один ход
    for row in range(ROWS):
        for col in range(COLUMNS):
            # Горизонтальные позиции
            for offset in range(-3, 1):
                if col + offset >= 0 and col + offset + 3 < COLUMNS:
                    pattern = [board[row][(col + offset + i) % COLUMNS] for i in range(4)]
                    if pattern.count(symbol) == 3 and pattern.count(' ') == 1:
                        score += 50
            
            # Вертикальные позиции
            if row + 3 < ROWS:
                pattern = [board[row + i][col] for i in range(4)]
                if pattern.count(symbol) == 3 and pattern.count(' ') == 1:
                    score += 50
            
            # Диагональные позиции (вправо вниз)
            if row + 3 < ROWS and col + 3 < COLUMNS:
                pattern = [board[row + i][(col + i) % COLUMNS] for i in range(4)]
                if pattern.count(symbol) == 3 and pattern.count(' ') == 1:
                    score += 50
            
            # Диагональные позиции (вправо вверх)
            if row - 3 >= 0 and col + 3 < COLUMNS:
                pattern = [board[row - i][(col + i) % COLUMNS] for i in range(4)]
                if pattern.count(symbol) == 3 and pattern.count(' ') == 1:
                    score += 50
    
    return score

def count_patterns(board, symbol, pattern_length):
    count = 0
    # Проверка горизонталей
    for row in range(ROWS):
        for col in range(COLUMNS - pattern_length + 1):
            if all(board[row][col + i] == symbol for i in range(pattern_length)):
                count += 1

    # Проверка вертикалей
    for col in range(COLUMNS):
        for row in range(ROWS - pattern_length + 1):
            if all(board[row + i][col] == symbol for i in range(pattern_length)):
                count += 1

    # Проверка диагоналей (вправо вниз)
    for row in range(ROWS - pattern_length + 1):
        for col in range(COLUMNS - pattern_length + 1):
            if all(board[row + i][col + i] == symbol for i in range(pattern_length)):
                count += 1

    # Проверка диагоналей (вправо вверх)
    for row in range(pattern_length - 1, ROWS):
        for col in range(COLUMNS - pattern_length + 1):
            if all(board[row - i][col + i] == symbol for i in range(pattern_length)):
                count += 1

    return count

def evaluate_board(board, symbol):
    score = 0
    opponent_symbol = 'O' if symbol == 'X' else 'X'
    
    # Проверка на победу
    if check_win(board, symbol):
        score += 100
    elif check_win(board, opponent_symbol):
        score -= 100
    
    # Дополнительные условия для оценки доски
    score += 10 * count_patterns(board, symbol, 3)  # +10 за каждую открытую тройку
    score += 5 * count_patterns(board, symbol, 2)   # +5 за каждую открытую двойку
    
    # Учитываем "почти победные" позиции
    score += evaluate_almost_winning_positions(board, symbol)
    
    return score

# Интеграция Минимакса в ход бота
def bot_move(board, turn):
    depth = 1000 # Пример глубины поиска
    score, col = minimax(board, depth, -float('inf'), float('inf'), True, turn)
    print(f"Bot move: col={col}, score={score}")  # Для отладки
    if col is None:  # Если minimax не нашел выгодного хода
        # Проверяем каждую колонку на наличие хотя бы одной свободной ячейки
        available_cols = [c for c in range(COLUMNS) if any(board[r][c] == ' ' for r in range(ROWS))]
        if available_cols:  # Если есть доступные колонки
            col = random.choice(available_cols)
            print(f"Random move: col={col}")
        else:  # Если нет доступных ходов
            print("No available moves.")
            return False
    if col is not None:
        apply_gravity(board, col, turn)
        return True
    return False

# Основной игровой цикл
def main():
    global board, player_symbol, bot_symbol
    board = [[' ' for _ in range(COLUMNS)] for _ in range(ROWS)]
    turn = player_symbol
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and turn != bot_symbol:
                x, y = event.pos
                col = x // CELL_SIZE
                if apply_gravity(board, col, turn):
                    if check_win(board, turn):
                        show_end_game_screen(turn)
                        running = False
                    turn = bot_symbol if turn == player_symbol else player_symbol
            elif turn == bot_symbol:
                bot_move(board, turn)
                if check_win(board, turn):
                    show_end_game_screen(turn)
                    running = False
                turn = player_symbol if turn == bot_symbol else bot_symbol
        draw_board(board)
        pygame.display.flip()

def restart_game():
    global board, player_symbol, bot_symbol
    player_symbol = None
    bot_symbol = None
    board = [[' ' for _ in range(COLUMNS)] for _ in range(ROWS)]
    choose_symbol_screen()

def quit_game():
    pygame.quit()
    sys.exit()

def show_end_game_screen(winner):
    screen.fill(BG_COLOR)
    if winner == player_symbol:
        message = "Поздравляем! Вы выиграли."
    elif winner == bot_symbol:
        message = "К сожалению, вы проиграли."
    else:
        message = "Ничья!"
    draw_text(message, FONT, (255, 255, 255), screen, WIDTH / 2, HEIGHT / 2 - 50)

    # Отображаем кнопки и ждем действия пользователя
    while True:
        draw_button("Играть заново", 150, HEIGHT / 2 + 50, 200, 50, (0, 255, 0), (0, 200, 0))
        draw_button("Выйти", WIDTH - 350, HEIGHT / 2 + 50, 200, 50, (255, 0, 0), (200, 0, 0))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                if 150 < mouse_x < 350 and HEIGHT / 2 + 50 < mouse_y < HEIGHT / 2 + 100:
                    restart_game()
                    return
                elif WIDTH - 350 < mouse_x < WIDTH - 150 and HEIGHT / 2 + 50 < mouse_y < HEIGHT / 2 + 100:
                    pygame.quit()
                    sys.exit()

if __name__ == "__main__":
    choose_symbol_screen()
