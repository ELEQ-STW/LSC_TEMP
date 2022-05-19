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

        modes: dict = dict(
            SLEEP=0x00,
            FORCED=0x01,
            NORMAL=0x03,
        )
        return modes[modes.keys()[mode]]

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

        filter: dict = dict(
            OFF=0x00,
            FILTER2=0x01,
            FILTER4=0x02,
            FILTER8=0x03,
            FILTER16=0x04,
        )
        return filter[filter.keys()[mode]]

    # Oversampling modes [CHAPTER 3.3]
    def oversamplingMode(self, pressure: int, temperature: int) -> tuple[int]:
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

        p: dict = dict(
            SKIP=0x00,
            OSx1=0x01,
            OSx2=0x02,
            OSx4=0x03,
            OSx8=0x04,
            OSx16=0x05,
        )
        t: dict = dict(
            SKIP=0x00,
            OSx1=0x01,
            OSx2=0x02,
            OSx4=0x03,
            OSx8=0x04,
            OSx16=0x05,
        )
        return p[p.keys()[pressure]], t[t.keys()[temperature]]
    
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

        standby: dict = dict(
            _500US=0x00,
            _62_5MS=0x01,
            _125MS=0x02,
            _250MS=0x03,
            _500MS=0x04,
            _1S=0x05,
            _2S=0x06,
            _4S=0x07,
        )
        return standby[standby.keys()[time]]
