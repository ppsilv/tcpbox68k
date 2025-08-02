#!/usr/bin/python3
import os  # Adicione esta linha
import time
from PyQt6.QtCore import QObject, pyqtSignal


class XMODEM_Transfer(QObject):

    def __init__(self):
        super().__init__()
        self.cancelled = False
        self.transfer_in_progress = False

        # Máquina de estados
        self.state = 'IDLE'  # Estados possíveis: IDLE, WAIT_NAK, SEND_BLOCK, WAIT_ACK, WAIT_EOT_ACK
        self.current_block = 0
        self.retry_count = 0
        self.total_blocks = 0
        self.current_block_data = None

        # Constantes XMODEM
        self.SOH = 0x01
        self.EOT = 0x04
        self.ACK = 0x06
        self.NAK = 0x15
        self.CAN = 0x18
        self.timeout = 50
        self.retries = 10

    def init_xmodem (_):
        print("xmodem initiated...");
        """ Function doc """
        
