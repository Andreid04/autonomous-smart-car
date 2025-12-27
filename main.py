import lgpio
chip = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(chip, 17, 0)  # test single pin
lgpio.gpio_claim_output(chip, 18, 0)  
lgpio.gpio_claim_output(chip, 22, 0)  
lgpio.gpio_claim_output(chip, 23, 0)  
lgpio.gpio_claim_output(chip, 12, 0) 
lgpio.gpio_claim_output(chip, 13, 0)   

for p in [17,18,22,23,12,13]:
    val = lgpio.gpio_read(chip, p)
    print(f"Pin {p} = {val}")

lgpio.gpio_write(chip, 17, 1)
val = lgpio.gpio_read(chip, 17)
print(f"After setting, Pin 17 = {val}")