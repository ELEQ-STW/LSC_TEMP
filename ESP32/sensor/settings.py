# Standard micropython libraries
# None

# Local modules and variables
# None


class SETTINGS:
    # Power modes [CHAPTER 3.6]
    def powerMode(self, mode: int) -> int:
        '''
        Different modes for the BMP280:
        - Sleep:  `int 0`
        - Forced: `int 1`
        - Normal: `int 2`
        '''
        # Check if the value set for mode is valid.
        assert 0 <= mode <= 2

        modes: tuple = tuple(
            0x00,  # Sleep
            0x01,  # Forced
            0x03,  # Normal
        )
        return modes[mode]

    # Filter (IIR) modes [CHAPTER 3.3.3]
    def iirMode(self, mode: int) -> int:
        '''
        Different IIR (Infinite Impulse Response) modes for the BMP280:
        - OFF:       `int 0`
        - FILTER 2:  `int 1`
        - FILTER 4:  `int 2`
        - FILTER 8:  `int 3`
        - FILTER 16: `int 4`
        '''
        # Check if the value set for mode is valid
        assert 0 <= mode <= 4

        filter: tuple = tuple(
            0x00,  # Filter OFF
            0x01,  # Filter 2
            0x02,  # Filter 4
            0x03,  # Filter 8
            0x04,  # Filter 16
        )
        return filter[mode]

    # Oversampling modes [CHAPTER 3.3]
    def osMode(self, pressure: int, temperature: int) -> tuple[int]:
        '''
        Different oversampling modes for the BMP280:
        - Pressure:
            - SKIP:   `int 0`
            - OS x1:  `int 1`
            - OS x2:  `int 2`
            - OS x4:  `int 3`
            - OS x8:  `int 4`
            - OS x16: `int 5`
        - Temperature:
            - SKIP:   `int 0`
            - OS x1:  `int 1`
            - OS x2:  `int 2`
            - OS x4:  `int 3`
            - OS x8:  `int 4`
            - OS x16: `int 5`
        '''
        # Check if the values set for pressure and temperature are valid.
        assert 0 <= pressure <= 5 and 0 <= temperature <= 5 

        p: tuple = tuple(
            0x00,  # No oversampling
            0x01,  # Oversampling x1
            0x02,  # Oversampling x2
            0x03,  # Oversampling x4
            0x04,  # Oversampling x8
            0x05,  # Oversampling x16
        )
        t: tuple = tuple(
            0x00,  # No oversampling
            0x01,  # Oversampling x1
            0x02,  # Oversampling x2
            0x03,  # Oversampling x4
            0x04,  # Oversampling x8
            0x05,  # Oversampling x16
        )
        return p[pressure], t[temperature]
    
    # Standby settings [CHAPTER 3.6.3]
    def standbyTime(self, time: int) -> int:
        '''
        Different standby settings for the BMP280:
        - 500 us:  `int 0`
        - 62.5 ms: `int 1`
        - 125 ms:  `int 2`
        - 250 ms:  `int 3`
        - 500 ms:  `int 4`
        - 1 s:     `int 5`
        - 2 s:     `int 6`
        - 4 s:     `int 7`
        '''
        # Check if the value set for time is valid
        assert 0 <= time <= 7

        standby: tuple = tuple(
            0x00,  # Standby time: 500 microseconds
            0x01,  # Standby time: 62.5 milliseconds
            0x02,  # Standby time: 125 milliseconds
            0x03,  # Standby time: 250 milliseconds
            0x04,  # Standby time: 500 milliseconds
            0x05,  # Standby time: 1 second
            0x06,  # Standby time: 2 seconds
            0x07,  # Standby time: 4 seconds
        )
        return standby[time]
