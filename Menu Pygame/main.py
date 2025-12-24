import pygame, sys
import subprocess
from button import Button
import os

pygame.init()
def launch_game(game_path):
    pygame.mixer.music.stop()
    pygame.quit()

    arg = "on" if music_on else "off"
    subprocess.Popen([sys.executable, game_path, arg])
    sys.exit()

pygame.mixer.init()

music_on = True
pygame.mixer.music.load("Menu Pygame/assetss/menu_music.mp3")
pygame.mixer.music.set_volume(1)
pygame.mixer.music.play(-1)  # loop selamanya


SCREEN = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Menu")

BG = pygame.image.load("Menu Pygame/assetss/Background.png")

def get_font(size):
    return pygame.font.Font("Menu Pygame/assetss/font.ttf", size)

def play():
    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("black")

        PLAY_TEXT = get_font(45).render("This is the PLAY screen.", True, "White")
        PLAY_RECT = PLAY_TEXT.get_rect(center=(640, 260))
        SCREEN.blit(PLAY_TEXT, PLAY_RECT)

        PLAY_BACK = Button(image=None, pos=(640, 460), 
                            text_input="BACK", font=get_font(75), base_color="White", hovering_color="Green")

        PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        PLAY_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    main_menu()

        pygame.display.update()
    
def options():
    while True:
        SCREEN.blit(BG, (0, 0))
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        OPTIONS_TEXT = get_font(80).render("OPTIONS", True, "#b68f40")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(640, 100))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)
        
        music_text = "Music : On" if music_on else "Music : Off"

        MUSIC_BUTTON = Button(
            image=pygame.image.load("Menu Pygame/assetss/Play Rect.png"),
            pos=(640, 260),
            text_input="Music",
            font=get_font(70),
            base_color="#d7fcd4",
            hovering_color="White"
        )
        OPTIONS_BACK = Button(image=None, pos=(640, 460), 
                            text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green")
        MUSIC_BUTTON.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)
        MUSIC_BUTTON.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if MUSIC_BUTTON.checkForInput(OPTIONS_MOUSE_POS):
                    toggle_music()
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()

        pygame.display.update()

def play_menu():
    while True:
        SCREEN.blit(BG, (0, 0))
        PLAYMENU_MOUSE_POS = pygame.mouse.get_pos()

        TITLE_TEXT = get_font(80).render("PLAY MODE", True, "#b68f40")
        TITLE_RECT = TITLE_TEXT.get_rect(center=(640, 100))
        SCREEN.blit(TITLE_TEXT, TITLE_RECT)

        PVP_BUTTON = Button(
            image=pygame.image.load("Menu Pygame/assetss/Play Rect.png"),
            pos=(640, 260),
            text_input="P V P",
            font=get_font(70),
            base_color="#d7fcd4",
            hovering_color="White"
        )

        BOT_BUTTON = Button(
            image=pygame.image.load("Menu Pygame/assetss/Play Rect.png"),
            pos=(640, 380),
            text_input="P V B",
            font=get_font(70),
            base_color="#d7fcd4",
            hovering_color="White"
        )

        BACK_BUTTON = Button(
            image=pygame.image.load("Menu Pygame/assetss/Quit Rect.png"),
            pos=(640, 520),
            text_input="BACK",
            font=get_font(65),
            base_color="#d7fcd4",
            hovering_color="White"
        )

        for button in [PVP_BUTTON, BOT_BUTTON, BACK_BUTTON]:
            button.changeColor(PLAYMENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if PVP_BUTTON.checkForInput(PLAYMENU_MOUSE_POS):
                    launch_game("pokemon game/turn based tcg.py")
                    # nanti isi game PVP di sini

                if BOT_BUTTON.checkForInput(PLAYMENU_MOUSE_POS):
                    launch_game("Battle-main/battle.py")
                    # nanti isi game BOT di sini

                if BACK_BUTTON.checkForInput(PLAYMENU_MOUSE_POS):
                    return  # kembali ke main menu

        pygame.display.update()


def toggle_music():
    global music_on
    music_on = not music_on

    if music_on:
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.stop()


def main_menu():
    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("Menu Pygame/assetss/Play Rect.png"), pos=(640, 250), 
                            text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("Menu Pygame/assetss/Options Rect.png"), pos=(640, 400), 
                            text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("Menu Pygame/assetss/Quit Rect.png"), pos=(640, 550), 
                            text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play_menu()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

main_menu()