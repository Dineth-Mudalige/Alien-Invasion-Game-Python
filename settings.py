

class Settings:
    """ A class to store all settings for Alien invasion"""
    def __init__(self):
        """Initializing the game's static settings """
        self.screen_width = 1360
        self.screen_height = 720
        self.bg_color = (233,233,233)

        #Ship settings
        self.ship_limit = 2

        # Bullet settings
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (200, 60, 60)
        self.msg_color = (144, 238, 144)
        self.bullets_count = 10

        #Aliens settings
        self.fleet_drop_speed = 10


        #How quickly the game speeds up
        self.speedup_scale = 1.2
        self.alien_speed_scale = 3   
        self.initialize_dynamic_settings()

        #How quickly the alien point values increase
        self.score_scale = 1.5

        # Level limit of the game
        self.levels_limit = 3

        # The values assigned to the String flags
        self.won = "WON"
        self.lost = "LOST"

    def initialize_dynamic_settings(self):
        self.ship_speed = 1.5
        self.bullet_speed = 1.2
        self.alien_speed = 0.02

        #scoring
        self.alien_points = 50

        # A fleet_direction of 1 represents right movement, -1 represents left movement.
        self.fleet_direction = 1

    def sensor_settings(self):
        self.sampling_rate = 1000
        self.channel_mask = "00001111"
        self.buffer_size = 1000
        self.device_mode = "_ExG"
        self.num_active_channels = 4



    def increase_speed(self):
        """Increase speed settings and score values"""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)
