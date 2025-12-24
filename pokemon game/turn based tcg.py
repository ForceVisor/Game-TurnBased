
import os
import pygame
import sys
import random
from dataclasses import dataclass
music_on = True
if len(sys.argv) > 1:
    music_on = sys.argv[1] == "on"

pygame.init()

W, H = 1080, 680
FPS = 60
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Turn Based Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 20)
bigfont = pygame.font.SysFont(None, 36)

#background deck select
bg_deck_select = pygame.image.load(
    "pokemon game/pocket_tc_assets/bg_deck_select.png"
).convert()

# background music
pygame.mixer.init()
pygame.mixer.music.load('pokemon game/pocket_tc_assets/battle tb music.mp3')
pygame.mixer.music.set_volume(1)
if music_on:
	pygame.mixer.music.play(-1)
else:
    pygame.mixer.music.stop()

# assets path (change this to your assets folder)
ASSETS_PATH = r"pokemon game\pocket_tc_assets"  # edit if needed

# images dict
images = {}

def try_load_assets():
    global images
    images = {}
    # include card_support.png
    files = [
        'card_charizard_a.png','card_charizard_b.png','card_charizard_c.png',
        'card_pikachu_a.png','card_pikachu_b.png','card_pikachu_c.png',
        'card_blastoise_a.png','card_blastoise_b.png','card_blastoise_c.png',
        'card_support.png',  # healer/support unified image
        'heal.png','shield.png','buff.png',
        'deck_charizard.png','deck_pikachu.png','deck_blastoise.png',
        'button_attack.png','button_special.png','button_support.png'
    ]
    for name in files:
        try:
            path = os.path.join(ASSETS_PATH, name)
            images[name] = pygame.image.load(path).convert_alpha()
        except Exception:
            images[name] = None

try_load_assets()

# Data models 
@dataclass
class Card:
    name: str
    hp: int
    max_hp: int
    atk: int
    defense: int
    special_cost: int
    special_ready: bool = False
    shield: int = 0
    buff_atk: int = 0
    alive: bool = True
    owner: int = 0  # 1 or 2
    is_support: bool = False
    support_heal: int = 0  # heal amount when using heal action

    def receive_damage(self, dmg):
        if self.shield > 0:
            blocked = min(self.shield, dmg)
            self.shield -= blocked
            dmg -= blocked
        if dmg > 0:
            self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def heal(self, amount):
        if not self.alive:
            return
        self.hp = min(self.max_hp, self.hp + amount)

    def effective_atk(self):
        return max(1, self.atk + self.buff_atk)

@dataclass
class SupportCard:
    name: str
    kind: str  # 'heal', 'shield', 'buff'
    value: int
    uses: int = 1

@dataclass
class Deck:
    name: str
    cards: list
    supports: list

# Deck factories 
def make_charizard_deck(owner):
    cards = [
        Card('Charizard-A', 78, 78, 24, 6, special_cost=4, owner=owner),
        Card('Charizard-B', 70, 70, 22, 8, special_cost=4, owner=owner),
        # third card is a healer/support card
        Card('Charizard-Healer', 50, 50, 6, 5, special_cost=1, owner=owner, is_support=True, support_heal=20),
    ]
    supports = [SupportCard('Flame Heal', 'heal', 22, uses=1), SupportCard('Rage Boost', 'buff', 6, uses=1)]
    return Deck('Charizard', cards, supports)

def make_pikachu_deck(owner):
    cards = [
        Card('Pikachu-A', 62, 62, 35, 4, special_cost=2, owner=owner),
        Card('Pikachu-B', 57, 57, 30, 5, special_cost=2, owner=owner),
        Card('Pikachu-Healer', 48, 48, 5, 4, special_cost=1, owner=owner, is_support=True, support_heal=18),
    ]
    supports = [SupportCard('Quick Heal', 'heal', 18, uses=1), SupportCard('Spark Shield', 'shield', 18, uses=1)]
    return Deck('Pikachu', cards, supports)

def make_blastoise_deck(owner):
    cards = [
        Card('Blastoise-A', 110, 92, 17, 13, special_cost=3, owner=owner),
        Card('Blastoise-B', 115, 86, 16, 13, special_cost=3, owner=owner),
        Card('Blastoise-Healer', 70, 70, 7, 12, special_cost=1, owner=owner, is_support=True, support_heal=24),
    ]
    supports = [SupportCard('Safe Shell', 'shield', 30, uses=1), SupportCard('Tide Heal', 'heal', 20, uses=1)]
    return Deck('Blastoise', cards, supports)

# Game state 
class GameState:
    def __init__(self):
        self.phase = 'deck_select'  # deck_select, battle, ended
        self.player_turn = 1
        self.decks_chosen = {1: None, 2: None}
        self.decks_ready = 0
        self.selected_card = None
        self.energy = {1: 0, 2: 0}
        self.points = {1: 0, 2: 0}
        self.turn_counter = {1: 0, 2: 0}
        self.win = None
        self.message = ''
        # modes
        self._awaiting_attack = False
        self._awaiting_heal = False
        # QUIZ
        self.turn_counter = 0
        self.quiz_active = False
        self.quiz_question = ""
        self.quiz_answer = 0
        self.quiz_input = ""
        self.quiz_timer = 10
        self.quiz_start_ticks = 0

    def reset_for_battle(self):
        self.phase = 'battle'
        self.player_turn = 1
        self.selected_card = None
        self.energy = {1: 1, 2: 1}
        self.points = {1: 0, 2: 0}
        self.win = None
        self.message = 'Player 1 turn'
        self._awaiting_attack = False
        self._awaiting_heal = False

state = GameState()

# drawing helpers 
def draw_text(surf, text, x, y, f=font, center=False, color=(255,255,255)):
    img = f.render(text, True, color)
    r = img.get_rect()
    if center:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    surf.blit(img, r)

CARD_W = 120
CARD_H = 200
CARD_MARGIN = 36
PLAYER_Y = H - 260
ENEMY_Y = 80

def card_positions_for_owner(owner):
    y = PLAYER_Y if owner == 1 else ENEMY_Y
    xs = []
    total_w = 3 * CARD_W + 2 * CARD_MARGIN
    start_x = (W - total_w) // 2
    for i in range(3):
        xs.append(pygame.Rect(start_x + i * (CARD_W + CARD_MARGIN), y, CARD_W, CARD_H))
    return xs

def draw_card(surface, card: Card, rect, small=False):
    # choose image key
    key = None
    lname = card.name.lower()

    if card.is_support:
        key = 'card_support.png'
    else:
        variant = None
        if '-' in lname:
            variant = lname.split('-')[-1].strip()
        elif ' ' in lname:
            variant = lname.split()[-1].strip()
        else:
            variant = lname[-1]
        if len(variant) > 1:
            variant = variant[0]

        if 'charizard' in lname:
            if variant == 'a':
                key = 'card_charizard_a.png'
            elif variant == 'b':
                key = 'card_charizard_b.png'
            else:
                key = 'card_charizard_c.png'
        elif 'pikachu' in lname:
            if variant == 'a':
                key = 'card_pikachu_a.png'
            elif variant == 'b':
                key = 'card_pikachu_b.png'
            else:
                key = 'card_pikachu_c.png'
        elif 'blastoise' in lname:
            if variant == 'a':
                key = 'card_blastoise_a.png'
            elif variant == 'b':
                key = 'card_blastoise_b.png'
            else:
                key = 'card_blastoise_c.png'

    img = images.get(key) if key else None

    # background / image
    pygame.draw.rect(surface, (245,245,245), rect, border_radius=10)
    if img:
        try:
            img_s = pygame.transform.smoothscale(img, (rect.width, rect.height))
            surface.blit(img_s, (rect.left, rect.top))
        except Exception:
            pygame.draw.rect(surface, (200,200,200), rect, border_radius=10)
    else:
        pygame.draw.rect(surface, (200,200,200), rect, border_radius=10)
        txt = font.render("ART", True, (0,0,0))
        tr = txt.get_rect(center=(rect.left + rect.width//2, rect.top + rect.height//2))
        surface.blit(txt, tr)

    # TOP STATS BAR (no name)
    stats_bg = pygame.Surface((rect.width, 36), pygame.SRCALPHA)
    stats_bg.fill((255,255,255,200))
    surface.blit(stats_bg, (rect.left, rect.top))

    # First line: HP
    txt_hp = font.render(f"HP: {card.hp}/{card.max_hp}", True, (0,0,0))
    surface.blit(txt_hp, (rect.left + 6, rect.top + 6))

    # Second line: HEAL for support cards, otherwise ATK & DEF
    if getattr(card, 'is_support', False):
        heal_amount = getattr(card, 'support_heal', 0)
        txt_second = font.render(f"HEAL: {heal_amount}", True, (0,0,0))
    else:
        txt_second = font.render(f"ATK:{card.effective_atk()}  DEF:{card.defense}", True, (0,0,0))
    surface.blit(txt_second, (rect.left + 6, rect.top + 20))

    # draw heal badge for support cards
    if getattr(card, 'is_support', False):
        heal_amount = getattr(card, 'support_heal', 0)
        badge_w, badge_h = 64, 24
        badge_x = rect.left + 6
        badge_y = rect.top + rect.height - badge_h - 6
        
        # transparent white bg
        s = pygame.Surface((badge_w, badge_h), pygame.SRCALPHA)
        s.fill((255,255,255,220))
        surface.blit(s, (badge_x, badge_y))
        txt_badge = font.render(f"HEAL {heal_amount}", True, (0,0,0))
        tb = txt_badge.get_rect(center=(badge_x + badge_w//2, badge_y + badge_h//2))
        surface.blit(txt_badge, tb.topleft)

    # shield indicator
    if card.shield > 0:
        txt_sh = font.render(f"Sld:{card.shield}", True, (0,0,0))
        surface.blit(txt_sh, (rect.right - txt_sh.get_width() - 6, rect.top + 6))

    # defeated overlay
    if not card.alive:
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        s.fill((0,0,0,160))
        surface.blit(s, (rect.left, rect.top))
        txt = bigfont.render("DEFEATED", True, (255,255,255))
        r = txt.get_rect(center=rect.center)
        surface.blit(txt, r)



    # name & stats strip
# TOP STATS BAR
    stats_bg = pygame.Surface((rect.width, 32), pygame.SRCALPHA)
    stats_bg.fill((255,255,255,200))
    surface.blit(stats_bg, (rect.left, rect.top))

    txt_hp = font.render(f"HP: {card.hp}/{card.max_hp}", True, (0,0,0))
    surface.blit(txt_hp, (rect.left + 6, rect.top + 6))

    txt_stats = font.render(f"ATK:{card.effective_atk()}  DEF:{card.defense}", True, (0,0,0))
    surface.blit(txt_stats, (rect.left + 6, rect.top + 18))


    if card.shield > 0:
        txt_sh = font.render(f"Sld:{card.shield}", True, (0,0,0))
        surface.blit(txt_sh, (rect.right - txt_sh.get_width() - 6, rect.top + 6))

    if not card.alive:
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        s.fill((0,0,0,160))
        surface.blit(s, (rect.left, rect.top))
        txt = bigfont.render("DEFEATED", True, (255,255,255))
        r = txt.get_rect(center=rect.center)
        surface.blit(txt, r)

# UI drawing - deck select & battle
def draw_button(rect, label, enabled=True, danger=False):
    if not enabled:
        color = (70,70,70)          # disabled (abu-abu)
    elif danger:
        color = (160,70,70)         # end turn (merah)
    else:
        color = (100,100,120)       # normal
    pygame.draw.rect(screen, color, rect, border_radius=6)
    draw_text(screen, label, rect.centerx, rect.centery, center=True)

# card selection screen
def draw_deck_select():
    bg = pygame.transform.scale(bg_deck_select, (W, H))
    screen.blit(bg, (0, 0))
    draw_text(
        screen,
        f"Select a deck for Player {state.decks_ready+1}",
        W//2,
        100,            
        f=bigfont,
        center=True
    )

    decks = ['Charizard', 'Pikachu', 'Blastoise']
    box_w, box_h = 240, 160
    start_x = (W - (3*box_w + 2*40))//2
    mx,my = pygame.mouse.get_pos()
    for i,(name) in enumerate(decks):
        r = pygame.Rect(start_x + i*(box_w+40), 180, box_w, box_h)
        pygame.draw.rect(screen, (70,70,90), r, border_radius=10)

        draw_text(screen, f" {name}", r.centerx, r.centery, f=bigfont, center=True)
        draw_text(screen, "Click to choose", r.centerx, r.bottom-28, center=True)
        if r.collidepoint(mx,my):
            pygame.draw.rect(screen, (200,200,200), r, 3)

    if state.decks_ready > 0:
        draw_text(screen, 'Deck chosen for Player 1. Now Player 2 choose.', W//2, H-40, center=True)

def draw_battle():
    # banner player turn
    screen.fill((12,18,40))
    banner_h = 44
    banner_color = (70,120,200) if state.player_turn == 1 else (200,80,80)
    pygame.draw.rect(screen, banner_color, (0, 0, W, banner_h))
    draw_text(
        screen,
        f"PLAYER {state.player_turn} TURN",
        W//2,
        banner_h//2,
        f=bigfont,
        center=True
    )


    # points left, player turn & energy info, and message below
    draw_text(screen, f"P1 Points: {state.points[1]}    P2 Points: {state.points[2]}", 20, 10)
   
    if state.message and not state.message.lower().startswith("player"):
        draw_text(screen, state.message, W//2, 56, center=True)

    p1_positions = card_positions_for_owner(1)
    p2_positions = card_positions_for_owner(2)

    # draw enemy (player 2) cards
    enemy_deck = state.decks_chosen[2]
    for i, card in enumerate(enemy_deck.cards):
        draw_card(screen, card, p2_positions[i])
        if state.selected_card is card:
             pygame.draw.rect(screen, (255,255,0), p2_positions[i], 3, border_radius=8)

    #ENERGY INFO PANEL
    energy_y = (PLAYER_Y + ENEMY_Y + CARD_H) // 2 - 24

    box_w = 320
    box_h = 44
    box_x = (W - box_w) // 2

    pygame.draw.rect(
        screen,
        (30, 30, 45),
        (box_x, energy_y, box_w, box_h),
        border_radius=10
    )

    MAX_ENERGY = 5

    p1_energy_text = "MAX" if state.energy[1] >= MAX_ENERGY else str(state.energy[1])
    p2_energy_text = "MAX" if state.energy[2] >= MAX_ENERGY else str(state.energy[2])

    draw_text(
        screen,
        f"Player 1 Energy: {p1_energy_text}   |   Player 2 Energy: {p2_energy_text}",
        W//2,
        energy_y + box_h // 2,
        center=True,
        color=(220,220,220)
    )

    # draw player (player 1) cards
    player_deck = state.decks_chosen[1]
    for i, card in enumerate(player_deck.cards):
        draw_card(screen, card, p1_positions[i])
        if state.selected_card is card:
            pygame.draw.rect(screen, (255,255,0), p1_positions[i], 3, border_radius=8)

    # If awaiting heal, highlight valid ally targets (green)
    if state._awaiting_heal:
        healer = state.selected_card
        if healer and healer.is_support and healer.owner == state.player_turn:
            # select positions for the active player's allies
            pos_list = p1_positions if state.player_turn == 1 else p2_positions
            deck = state.decks_chosen[state.player_turn]
            for i, rect in enumerate(pos_list):
                target_card = deck.cards[i]
                if target_card.alive and target_card is not healer:
                    pygame.draw.rect(screen, (60,200,60), rect, 4, border_radius=8)

    # action buttons
    btn_w, btn_h = 150, 40
    bx = 40
    by = 220
    gap = 14

    global attack_btn, special_btn, support_btn, heal_btn, endturn_btn

    attack_btn  = pygame.Rect(bx, by + 0*(btn_h + gap), btn_w, btn_h)
    special_btn = pygame.Rect(bx, by + 1*(btn_h + gap), btn_w, btn_h)
    support_btn = pygame.Rect(bx, by + 2*(btn_h + gap), btn_w, btn_h)
    heal_btn    = pygame.Rect(bx, by + 3*(btn_h + gap), btn_w, btn_h)
    endturn_btn = pygame.Rect(bx, by + 4*(btn_h + gap), btn_w, btn_h)

    # determine if buttons are enabled
    can_act = (
        state.selected_card is not None
        and state.player_turn == 1
        and not state.quiz_active
    )
    draw_button(attack_btn,  "Attack",  enabled=can_act)
    draw_button(special_btn, "Special", enabled=can_act)
    draw_button(support_btn, "Support", enabled=can_act)
    draw_button(heal_btn,    "Heal",    enabled=can_act)
    draw_button(endturn_btn, "End Turn", enabled=not state.quiz_active, danger=True)

    pygame.draw.rect(screen, (100,100,120), attack_btn, border_radius=6)
    pygame.draw.rect(screen, (100,100,120), special_btn, border_radius=6)
    pygame.draw.rect(screen, (100,100,120), support_btn, border_radius=6)
    pygame.draw.rect(screen, (100,100,120), heal_btn, border_radius=6)
    pygame.draw.rect(screen, (120,60,60), endturn_btn, border_radius=6)

    draw_text(screen, 'Attack', attack_btn.centerx, attack_btn.centery, center=True)
    draw_text(screen, 'Special', special_btn.centerx, special_btn.centery, center=True)
    draw_text(screen, 'Support', support_btn.centerx, support_btn.centery, center=True)
    draw_text(screen, 'Heal', heal_btn.centerx, heal_btn.centery, center=True)
    draw_text(screen, 'End Turn', endturn_btn.centerx, endturn_btn.centery, center=True)

    # SUPPORT INFO PANEL
    sp_w = 220
    sp_x = W - sp_w - 16
    sp_y = 80
    line_h = 24

    supports = state.decks_chosen[state.player_turn].supports
    sp_h = 40 + len(supports) * line_h

    # background panel
    pygame.draw.rect(
        screen,
        (30,30,40),
        (sp_x, sp_y, sp_w, sp_h),
        border_radius=10
    )

    # title
    draw_text(
        screen,
        f"Supports (P{state.player_turn})",
        sp_x + 12,
        sp_y + 10
    )

    # list supports
    for i, s in enumerate(supports):
        draw_text(
            screen,
            f"{i+1}. {s.name} ({s.kind}) x{s.uses}",
            sp_x + 12,
            sp_y + 36 + i * line_h,
            color=(200,200,200)
        )

# Game logic 
def calc_damage(attacker: Card, defender: Card, special=False):
    base = attacker.effective_atk()
    if special:
        base += 8
    dmg = base - (defender.defense // 2)
    if dmg < 1:
        dmg = 1
    return dmg

def check_killed_and_award_points():
    for owner in (1,2):
        deck = state.decks_chosen[owner]
        for c in deck.cards:
            if not c.alive and getattr(c, '_counted', False) == False:
                state.points[3-owner] += 1
                c._counted = True
                state.message = f"Player {3-owner} scored!"
                if state.points[3-owner] >= 3:
                    state.win = 3-owner
                    state.phase = 'ended'

def end_turn():
    state.turn_counter += 1
    # quiz, gain energy, swap turn, reset selections/modes

    state.energy[state.player_turn] = min(5, state.energy[state.player_turn] + 1)

    if state.turn_counter > 0 and state.turn_counter % 3 == 0:
        start_quiz()
        state.message = f"Player {state.player_turn} QUIZ TIME!"
    else:
        switch_player()

def switch_player():
    state.player_turn = 3 - state.player_turn
    state.selected_card = None
    state._awaiting_attack = False
    state._awaiting_heal = False
    state.message = f"Player {state.player_turn} turn"

def use_support(player, support_idx, target_card=None):
    supports = state.decks_chosen[player].supports
    if support_idx < 0 or support_idx >= len(supports):
        return False
    s = supports[support_idx]
    if s.uses <= 0:
        state.message = 'Support not available'
        return False
    if s.kind == 'heal':
        if target_card is None:
            alive_cards = [c for c in state.decks_chosen[player].cards if c.alive]
            if not alive_cards:
                return False
            target = min(alive_cards, key=lambda c: c.hp)
        else:
            target = target_card
        target.heal(s.value)
        state.message = f'{s.name} used on {target.name}'
    elif s.kind == 'shield':
        if target_card is None:
            alive_cards = [c for c in state.decks_chosen[player].cards if c.alive]
            if not alive_cards:
                return False
            target = random.choice(alive_cards)
        else:
            target = target_card
        target.shield += s.value
        state.message = f'{s.name} added to {target.name}'
    elif s.kind == 'buff':
        alive_cards = [c for c in state.decks_chosen[player].cards if c.alive]
        if not alive_cards:
            return False
        target = random.choice(alive_cards)
        target.buff_atk += s.value
        state.message = f'{s.name} buffed {target.name}'
    s.uses -= 1
    return True

def simple_ai_take_turn(player):
    deck = state.decks_chosen[player]
    opp = state.decks_chosen[3-player]
    attackers = [c for c in deck.cards if c.alive]
    targets = [c for c in opp.cards if c.alive]
    if not attackers or not targets:
        end_turn()
        return
    a = random.choice(attackers)
    t = random.choice(targets)
    dmg = calc_damage(a, t, special=False)
    t.receive_damage(dmg)
    state.message = f"AI Player {player}: {a.name} hit {t.name} for {dmg}"
    check_killed_and_award_points()
    end_turn()

# Event handlers
def handle_deck_select_click(mx, my):
    box_w, box_h = 240, 160
    start_x = (W - (3*box_w + 2*40))//2
    for i, factory in enumerate((make_charizard_deck, make_pikachu_deck, make_blastoise_deck)):
        r = pygame.Rect(start_x + i*(box_w+40), 120, box_w, box_h)
        if r.collidepoint(mx, my):
            owner = state.decks_ready + 1
            deck = factory(owner)
            state.decks_chosen[owner] = deck
            state.decks_ready += 1
            state.message = f"Player {owner} selected {deck.name}"
            if state.decks_ready >= 2:
                state.reset_for_battle()
            return

def handle_battle_click(mx, my):
    # Buttons
    if attack_btn.collidepoint(mx,my):
        if state.selected_card is None:
            state.message = 'Select your card first'
            return
        # Attack flow: enter attack selection mode
        state._awaiting_attack = True
        state._awaiting_heal = False
        state.message = 'Click enemy card to attack'
        return

    if heal_btn.collidepoint(mx,my):
        if state.selected_card is None:
            state.message = 'Select your card first'
            return
        c = state.selected_card
        if not c.is_support:
            state.message = 'Selected card cannot heal'
            return
        if c.owner != state.player_turn:
            state.message = 'Not your turn'
            return
        # Enter heal selection mode
        state._awaiting_heal = True
        state._awaiting_attack = False
        state.message = f'Click one friendly card to heal (by {c.name})'
        return

    if special_btn.collidepoint(mx,my):
        if state.selected_card is None:
            state.message = 'Select your card first'
            return
        c = state.selected_card
        if state.energy[state.player_turn] >= c.special_cost:
            targets = [t for t in state.decks_chosen[3-state.player_turn].cards if t.alive]
            if not targets:
                state.message = 'No targets'
                return
            t = random.choice(targets)
            dmg = calc_damage(c, t, special=True)
            t.receive_damage(dmg)
            state.energy[state.player_turn] -= c.special_cost
            state.message = f'{c.name} used Special on {t.name} for {dmg}'
            check_killed_and_award_points()
            end_turn()
        else:
            state.message = 'Not enough energy for special'
        return

    if support_btn.collidepoint(mx,my):
        supports = state.decks_chosen[state.player_turn].supports

        for i, s in enumerate(supports):
            if s.uses > 0:
                used = use_support(state.player_turn, i)
                if used:
                    end_turn()
                return

        state.message = "No support available"
        return


    if endturn_btn.collidepoint(mx,my):
        # cancel heal mode if any
        state._awaiting_heal = False
        end_turn()
        return

    # Prepare card positions
    p1_positions = card_positions_for_owner(1)
    p2_positions = card_positions_for_owner(2)

    # heal mode handling
    if state._awaiting_heal and state.selected_card:
        healer = state.selected_card
        if healer.owner == state.player_turn and healer.is_support:
            pos_list = p1_positions if state.player_turn == 1 else p2_positions
            deck = state.decks_chosen[state.player_turn]
            for i, rect in enumerate(pos_list):
                if rect.collidepoint(mx,my):
                    target = deck.cards[i]
                    if target is healer:
                        state.message = 'Cannot heal self'
                        return
                    if not target.alive:
                        state.message = 'Cannot heal defeated card'
                        return
                    target.heal(healer.support_heal)
                    state.message = f'{healer.name} healed {target.name} for {healer.support_heal}'
                    state._awaiting_heal = False
                    check_killed_and_award_points()
                    end_turn()
                    return
        # if clicked elsewhere when in heal mode, ignore and keep mode
        return

    # Normal card clicking & attack flows
    # Player1 own cards selection / Player2 attack target resolution
    for i, rect in enumerate(p1_positions):
        if rect.collidepoint(mx,my):
            c = state.decks_chosen[1].cards[i]
            # if it's Player1's turn -> select card
            if state.player_turn == 1:
                if not c.alive:
                    state.message = 'Card defeated'
                    return
                state.selected_card = c
                state._awaiting_heal = False
                state._awaiting_attack = False
                state.message = f'Selected {c.name}'
                return
            # else if player2 is awaiting attack target (P2 attacking P1)
            if state._awaiting_attack and state.selected_card and state.player_turn == 2:
                a = state.selected_card
                if not a.alive or not c.alive:
                    state.message = 'Invalid attack'
                    state._awaiting_attack = False
                    return
                dmg = calc_damage(a, c, special=False)
                c.receive_damage(dmg)
                state.message = f'{a.name} hit {c.name} for {dmg}'
                state._awaiting_attack = False
                check_killed_and_award_points()
                end_turn()
                return

    # Player1 clicking enemy targets when awaiting attack (P1 attacking P2)
    for i, rect in enumerate(p2_positions):
        if rect.collidepoint(mx,my):
            c = state.decks_chosen[2].cards[i]
            if state._awaiting_attack and state.selected_card and state.player_turn == 1:
                a = state.selected_card
                if not a.alive or not c.alive:
                    state.message = 'Invalid attack'
                    state._awaiting_attack = False
                    return
                dmg = calc_damage(a, c, special=False)
                c.receive_damage(dmg)
                state.message = f'{a.name} hit {c.name} for {dmg}'
                state._awaiting_attack = False
                check_killed_and_award_points()
                end_turn()
                return

    # Mirror controls for player 2 (select own cards)
    for i, rect in enumerate(p2_positions):
        if rect.collidepoint(mx,my):
            c = state.decks_chosen[2].cards[i]
            if state.player_turn == 2:
                if not c.alive:
                    state.message = 'Card defeated'
                    return
                state.selected_card = c
                state._awaiting_heal = False
                state._awaiting_attack = False
                state.message = f'Selected {c.name}'
                return
            # if player1 awaiting attack and clicked on p2 position this was handled above

    # Player2 attacking player1 when awaiting attack (already covered in loops above)
    # Nothing else to do


# MAIN LOOP
def main():
    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            #escape to quit
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            # MOUSE CLICK HANDLING
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if state.quiz_active:
                    continue
                mx,my = pygame.mouse.get_pos()
                if state.phase == 'deck_select':
                    handle_deck_select_click(mx,my)
                elif state.phase == 'battle':
                    handle_battle_click(mx,my)
                elif state.phase == 'ended':
                    # reset
                    state.phase = 'deck_select'
                    state.decks_chosen = {1: None, 2: None}
                    state.decks_ready = 0
                    state.message = ''

        # QUIZ INPUT HANDLING
            if state.quiz_active and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if state.quiz_input == str(state.quiz_answer):
                            apply_quiz_reward(True)
                        else:
                            apply_quiz_reward(False)
                    elif event.key == pygame.K_BACKSPACE:
                        state.quiz_input = state.quiz_input[:-1]
                    elif event.unicode.isdigit():
                        state.quiz_input += event.unicode

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if state.quiz_active: continue
                mx, my = pygame.mouse.get_pos()    

            
        if state.phase == 'deck_select':
            draw_deck_select()
        elif state.phase == 'battle':
            draw_battle()
            if state.quiz_active:
                draw_quiz_overlay()
        elif state.phase == 'ended':
            screen.fill((10,10,10))
            draw_text(screen, f"Player {state.win} WINS! Click to play again.", W//2, H//2, f=bigfont, center=True)


        pygame.display.flip()

    pygame.quit()
    sys.exit()

# QUIZ FUNCTIONS
def start_quiz():
    state.quiz_active = True
    num1 = random.randint(10, 20)
    num2 = random.randint(10, 30)
    state.quiz_question = f"{num1} x {num2} = ?"
    state.quiz_answer = num1 * num2
    state.quiz_input = ""
    state.quiz_timer = 15 
    state.quiz_start_ticks = pygame.time.get_ticks()
    state.quiz_result_msg = ""

def apply_quiz_reward(success):
    if success:
        deck = state.decks_chosen[state.player_turn]
        for c in deck.cards:
            if c.alive:
                c.heal(20)
        state.message = f"QUIZ SUCCESS! +20 HP for all Player {state.player_turn} allies!"
    else:
        state.message = "QUIZ FAILED"
    
    state.quiz_active = False

    state.player_turn = 3 - state.player_turn
    state.selected_card = None
    state._awaiting_attack = False
    state._awaiting_heal = False

# POP UP QUIZ
def draw_quiz_overlay():
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    box_r = pygame.Rect(W//2 - 200, H//2 - 150, 400, 300)
    pygame.draw.rect(screen, (50, 50, 70), box_r, border_radius=15)
    pygame.draw.rect(screen, (255, 255, 255), box_r, 3, border_radius=15)
    
    elapsed = (pygame.time.get_ticks() - state.quiz_start_ticks) // 1000
    time_left = max(0, state.quiz_timer - elapsed)
    
    draw_text(screen, f"BONUS QUIZ for Player {state.player_turn}!", W//2, H//2 - 110, f=bigfont, center=True, color=(255, 215, 0))
    draw_text(screen, f"Time remaining: {time_left}s", W//2, H//2 - 70, center=True)
    draw_text(screen, state.quiz_question, W//2, H//2 - 20, f=bigfont, center=True)
    
    input_r = pygame.Rect(W//2 - 100, H//2 + 20, 200, 50)
    pygame.draw.rect(screen, (30, 30, 30), input_r, border_radius=5)
    draw_text(screen, state.quiz_input + "_", W//2, H//2 + 45, f=bigfont, center=True)
    
    draw_text(screen, "Input your answer & Press ENTER", W//2, H//2 + 90, center=True, color=(180, 180, 180))

    if time_left <= 0:
        apply_quiz_reward(False)

if __name__ == '__main__':
    main()
