import lgpio
import time
import threading

class MotorController:
    def __init__(self):
        self.chip = lgpio.gpiochip_open(0)
        
        # BCM pin numbers
        self.LEFT_FWD = 17
        self.LEFT_BWD = 18
        self.RIGHT_FWD = 22
        self.RIGHT_BWD = 23
        self.ENA = 12   
        self.ENB = 13   
        
        # Current speed state
        self.speed = 0.4 # 40%
        self.pwm_freq = 1000 # 1kHz

        # Claim pins
        lgpio.gpio_claim_output(self.chip, self.ENA, 0)
        lgpio.gpio_claim_output(self.chip, self.ENB, 0)
        for p in [self.LEFT_FWD, self.LEFT_BWD, self.RIGHT_FWD, self.RIGHT_BWD]:
            lgpio.gpio_claim_output(self.chip, p, 0)

        # Initialize Hardware PWM on ENA and ENB
        self._update_hardware_pwm()

    def _update_hardware_pwm(self):
        """Updates the physical PWM pulse based on self.speed"""
        duty_cycle_percent = self.speed * 100
        lgpio.tx_pwm(self.chip, self.ENA, self.pwm_freq, duty_cycle_percent)
        lgpio.tx_pwm(self.chip, self.ENB, self.pwm_freq, duty_cycle_percent)

    def change_speed(self, delta):
        """Handles inc_speed and dec_speed logic"""
        if delta > 0:
            self.speed = min(self.speed + 0.1, 0.7) # it blows up over 70%
        else:
            self.speed = max(self.speed - 0.1, 0.2)
        
        # Immediately push the new speed to the hardware
        self._update_hardware_pwm()

    def stop_all(self):
        for pin in [self.LEFT_FWD, self.LEFT_BWD, self.RIGHT_FWD, self.RIGHT_BWD]:
            lgpio.gpio_write(self.chip, pin, 0)

    def forward(self):
        lgpio.gpio_write(self.chip, self.LEFT_BWD, 0)
        lgpio.gpio_write(self.chip, self.RIGHT_BWD, 0)
        lgpio.gpio_write(self.chip, self.LEFT_FWD, 1)
        lgpio.gpio_write(self.chip, self.RIGHT_FWD, 1)

    def backward(self):
        lgpio.gpio_write(self.chip, self.LEFT_FWD, 0)
        lgpio.gpio_write(self.chip, self.RIGHT_FWD, 0)
        lgpio.gpio_write(self.chip, self.LEFT_BWD, 1)
        lgpio.gpio_write(self.chip, self.RIGHT_BWD, 1)

    def turn_left(self):
        lgpio.gpio_write(self.chip, self.LEFT_FWD, 0)
        lgpio.gpio_write(self.chip, self.LEFT_BWD, 1)
        lgpio.gpio_write(self.chip, self.RIGHT_BWD, 0)
        lgpio.gpio_write(self.chip, self.RIGHT_FWD, 1)

    def turn_right(self):
        lgpio.gpio_write(self.chip, self.RIGHT_FWD, 0)
        lgpio.gpio_write(self.chip, self.RIGHT_BWD, 1)
        lgpio.gpio_write(self.chip, self.LEFT_BWD, 0)
        lgpio.gpio_write(self.chip, self.LEFT_FWD, 1)