import re
from abc import ABC, abstractmethod

class PDU(ABC):
    def __init__(self, payload: str):
        if type(self) is PDU:
            raise TypeError("Nelze vytvářet instance abstraktní třídy PDU přímo.")
        
        self._payload = payload

    @property
    def payload(self) -> str:
        return self._payload

    @payload.setter
    def payload(self, val: str):
        self._payload = val

    @abstractmethod
    def isValid(self) -> bool:
        pass


class EthFrame(PDU):
    def __init__(self, dmac: str, smac: str, type_id: int, payload: str, fcs: int = None):
        super().__init__(payload)
        
        if not self.isValidMac(dmac) or not self.isValidMac(smac):
            raise ValueError("Neplatný formát MAC adresy.")
            
        self._dmac = dmac
        self._smac = smac
        self._type = type_id
        
        if fcs is None:
            self._fcs = self.calculateFcs()
        else:
            self._fcs = fcs

    @staticmethod
    def isValidMac(mac: str) -> bool:
        """Ověří, zda MAC adresa odpovídá standardnímu hexadecimálnímu tvaru."""
        pattern = r"^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$"
        return bool(re.match(pattern, mac))

    def calculateFcs(self) -> int:
        """Vypočítá kontrolní součet (Hash) z hlavičky a payloadu."""
        combined_data = f"{self._dmac}{self._smac}{self._type}{self.payload}"
        return sum(ord(char) for char in combined_data)

    def _recalculateFcs(self):
        """Privátní pomocná metoda pro aktualizaci FCS."""
        self._fcs = self.calculateFcs()

    def isValid(self) -> bool:
        """Porovná uložené FCS s aktuálně vypočítaným."""
        return self._fcs == self.calculateFcs()

    def corruptData(self):
        """Úmyslně poškodí data pro demonstrační účely."""
        self._payload = "!!! DATA CORRUPTED !!!"
        self._fcs = -1  

    @property
    def dmac(self): return self._dmac
    
    @dmac.setter
    def dmac(self, val):
        if self.isValidMac(val):
            self._dmac = val
            self._recalculateFcs()
        else:
            raise ValueError("Neplatný formát MAC adresy.")

    @property
    def smac(self): return self._smac

    @smac.setter
    def smac(self, val):
        if self.isValidMac(val):
            self._smac = val
            self._recalculateFcs()
        else:
            raise ValueError("Neplatný formát MAC adresy.")

    @property
    def type(self): return self._type

    @type.setter
    def type(self, val):
        self._type = val
        self._recalculateFcs()

    @PDU.payload.setter
    def payload(self, val):
        self._payload = val
        self._recalculateFcs()

    @property
    def fcs(self):
        """Getter pro FCS (bez setteru)."""
        return self._fcs

    def __str__(self) -> str:
        valid_status = "OK" if self.isValid() else "CORRUPTED"
        return (f"[EthFrame] SRC: {self._smac} | DST: {self._dmac} | "
                f"TYPE: {hex(self._type)} | FCS: {self._fcs} | STATUS: {valid_status} | "
                f"DATA: {self.payload}")



if __name__ == "__main__":
    try:
        
        frame = EthFrame("AA:BB:CC:DD:EE:FF", "11:22:33:44:55:66", 0x0800, "Hello World")
        print("Původní rámec:")
        print(frame)

        
        frame.payload = "Nová data"
        print("\nPo změně payloadu (stále validní):")
        print(frame)

        
        frame.corruptData()
        print("\nPo volání corruptData():")
        print(frame)
        print(f"Je rámec validní? {frame.isValid()}")

    except Exception as e:
        print(f"Chyba: {e}")