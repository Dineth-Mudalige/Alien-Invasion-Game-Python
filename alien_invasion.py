""""    Creating an empty pygame window and responding to user input    """
import sys

import pygame

from time import sleep

from settings import Settings

from ship import Ship

from bullets import Bullet

from aliens import Alien

from game_stats import GameStats

from button import Button

from scoreboard import Scoreboard

from pygame.locals import *

import os

    
class AlienInvasion:
    """ Overall class to manage game assets and behavior """
    def __init__(self):
        """ Initialize the game, and create game resources  """
        pygame.init()

        self.settings = Settings()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        
        pygame.display.set_caption("Alien Invasion")    #  Setting the title of the game in the game window
        
        self.stats = GameStats(self)
        self.ship = Ship(self)  #Creating an instance of the ship class we imported

        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        
        self.__create_alien_fleet()

        #make the play button
        self.play_button = Button(self,"Play")

        #Create an instance to store game statistics and create a score board
        self.score_board = Scoreboard(self)
        
        self.status = ""

    def run_game(self):
        """ Start the main loop for the game """
        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets() 
                self._update_aliens()
                self._fire_bullet()
            self._update_screen()  

    def _check_events(self):
        """Respond to keypresses and mouse events"""
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    os._exit(0)

                elif event.type == pygame.KEYDOWN:
                    self._check_keydown_events(event)
                    
                elif event.type == pygame.KEYUP:
                    self._check_keyup_events(event)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self._check_play_button(mouse_pos)


    def _check_play_button(self,mouse_pos):
        """Check if the the player is clicking on the play button before starting a new game """
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            #Reset the game satistics and settings
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self._start_game()
            self.score_board.prep_score()
            self.score_board.prep_level()
            self.score_board.prep_ships()
            
            #Get rid of any bullets and aliens
            self.aliens.empty()
            self.bullets.empty()

            #Create a new fleet and center the ship
            self.__create_alien_fleet()
            self.ship.center_ship()

            #Hide the mouse cursor
            pygame.mouse.set_visible(False)


    """Function to start the game"""
    def _start_game(self):
        self.stats.game_active = True


    def _show_screen(self,msg):
        msg_font = pygame.font.Font(None, 80)
        msg_text = msg_font.render(msg, True, self.settings.msg_color)
        instructions_font = pygame.font.Font(None, 36)
        instructions_text = instructions_font.render("Press M to restart and Esc to exit", True, self.settings.msg_color)
        msg_text_rect = msg_text.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2))
        instructions_text_rect = instructions_text.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height - 40))
        self.screen.fill(self.settings.bg_color)  # Fill the screen with black
        self.screen.blit(msg_text, msg_text_rect)
        self.screen.blit(instructions_text, instructions_text_rect)
        pygame.display.flip()

    
    """ Function to check key down events  """
    def _check_keydown_events(self,event):
        if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
            os._exit(0)
        elif event.key == pygame.K_LEFT:
        #   Move the ship to the left
            self.ship.moving_left = True
            print("Moving left")
        elif event.key == pygame.K_RIGHT:
        #   Move the ship to the right
            self.ship.moving_right = True
            print("Moving right")   
        # elif event.key == pygame.K_SPACE:
        #     self._fire_bullet()
        elif event.key == pygame.K_SPACE:
            self.stats.game_active = False
        elif event.key == pygame.K_p:
            self.stats.game_active = True
        elif event.key == pygame.K_m:
            self.status = ""
            self.play_button.draw_button()
            pygame.mouse.set_visible(True)


    """ Function to check key up events  """
    def _check_keyup_events(self,event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False  


    def _fire_bullet(self):
        """ Create a new bullet and add it to the bullets group """  
        if len(self.bullets) < self.settings.bullets_count:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """Update bullet positions and get rid of old bullets"""
        #Update bullet positions
        self.bullets.update()

        #Delete old bullets
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        #   Check for   any bullets that have hit aliens
        # if so, get rid of the bullet and the alien
        collissions = pygame.sprite.groupcollide(self.bullets,self.aliens,True,True) 
        if not self.aliens:
            self._check_bullet_alien_collision()
            if self.stats.level > self.settings.levels_limit:
                self.status = self.settings.won
                self.stats.game_active = False
                
        if collissions:
            for aliens in collissions.values(): 
                self.stats.score += self.settings.alien_points * len(aliens)
                
            self.score_board.prep_score()
            self.score_board.check_high_score()

    def _check_bullet_alien_collision(self):
        #Destroy existing bullets and create new fleet
            self.bullets.empty()
            self.__create_alien_fleet()
            self.settings.increase_speed()

            #INcrease the level
            self.stats.level += 1
            self.score_board.prep_level()

    def _update_aliens(self):
        """Check if aliens are at any edge before updating entire fleet"""
        self._check_fleet_edges()
        self.aliens.update()

        #check for ship and aliens collisions
        if pygame.sprite.spritecollideany(self.ship,self.aliens):
            #Call the ship hit method
            self._ship_hit()

        #Check for aliens that reach the bottom
        self._check_aliens_bottom()


    def _ship_hit(self):
        """Respond to the ship being hit by an alien"""
        if self.stats.ships_left > 0:
            #Decrement ships left by 1
            self.stats.ships_left -= 1
            self.score_board.prep_ships()

            #Get rid of any remaining aliens and bullets
            self.aliens.empty()
            self.bullets.empty()

            #Create a new flit and center the ship
            self.__create_alien_fleet()
            self.ship.center_ship()

            #pause.
            sleep(0.5)
        else:
            self.status = self.settings.lost
            self.stats.game_active = False

    


    def __create_alien_fleet(self):
        """Create an alien and find how many aliens can fit in a single row"""
        alien = Alien(self)
        alien_width = alien.rect.width
        alien_height = alien.rect.height
        available_space_x = self.settings.screen_width - (2 * alien_width)  #   Amount of horizontal space we have
        number_aliens_x = available_space_x // (alien_width * 2)        #How many aliens can fit in a horizontal row

        #   Determine the number of rows of aliens that fit on the screen
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        # number_rows = available_space_y // (2 * alien_height)
        number_rows = self.stats.level + 1; 
        #   Creating the full fleet of aliens
        for row_number in range(number_rows):
            #   Creating first row of aliens
            for alien_number in range(number_aliens_x):
                self.__create_alien(alien_number,row_number)




    def __create_alien(self,alien_number,row_number):
        #Create an alien and place it in a row
        alien = Alien(self)
        alien_width = alien.rect.width
        alien_height = alien.rect.height
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.y = alien_height + 2 * alien_height * row_number
        alien.rect.x = alien.x
        self.aliens.add(alien)


    def _check_fleet_edges(self):
        """ Respond appropriately if any aliens have reached an edge"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break


    def _change_fleet_direction(self):
        """ Drop the entire fleet and change fleet's direction  """
        # for alien in self.aliens.sprites():
        #     alien.rect.y += self.settings.fleet_drop_speed
        # self.settings.fleet_direction *= -1
        pass


    def _check_aliens_bottom(self):
        """Check if any aliens reach the bottom """
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break

    def _update_screen(self):
        #   Update images on the screen, and flip to the new screen
        self.screen.fill(self.settings.bg_color)

        self.ship.blitme()

        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        self.aliens.draw(self.screen)

        #Draw the play button if the game is inactive
        if not self.stats.game_active:
            if self.status == self.settings.won:
                self._show_screen("Victory Achieved!")
            elif self.status == self.settings.lost:
                self._show_screen("Game Over!")
            else:
                self.play_button.draw_button()

        #Draw the score information
        self.score_board.show_score()

        pygame.display.flip()

if __name__ == '__main__':
    #   Make a game instance
    ai = AlienInvasion()
    ai.run_game()