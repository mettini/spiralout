"""RRDBNet (Real-ESRGAN x4) en torch puro.

Se escribe a mano en vez de instalar `realesrgan` porque ese paquete arrastra `basicsr`,
que no compila contra torch 2.11. La red es chica y estable desde 2018; los pesos
oficiales cargan tal cual contra estos nombres de modulo.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class BloqueDenso(nn.Module):
    """Cinco convoluciones donde cada una ve la salida de TODAS las anteriores."""

    def __init__(self, nf=64, gc=32):
        super().__init__()
        self.conv1 = nn.Conv2d(nf, gc, 3, 1, 1)
        self.conv2 = nn.Conv2d(nf + gc, gc, 3, 1, 1)
        self.conv3 = nn.Conv2d(nf + 2 * gc, gc, 3, 1, 1)
        self.conv4 = nn.Conv2d(nf + 3 * gc, gc, 3, 1, 1)
        self.conv5 = nn.Conv2d(nf + 4 * gc, nf, 3, 1, 1)
        self.act = nn.LeakyReLU(0.2, inplace=True)

    def forward(self, x):
        x1 = self.act(self.conv1(x))
        x2 = self.act(self.conv2(torch.cat((x, x1), 1)))
        x3 = self.act(self.conv3(torch.cat((x, x1, x2), 1)))
        x4 = self.act(self.conv4(torch.cat((x, x1, x2, x3), 1)))
        x5 = self.conv5(torch.cat((x, x1, x2, x3, x4), 1))
        return x5 * 0.2 + x            # el 0.2 es del paper: sin eso el residuo explota


class RRDB(nn.Module):
    def __init__(self, nf=64, gc=32):
        super().__init__()
        self.rdb1, self.rdb2, self.rdb3 = (BloqueDenso(nf, gc) for _ in range(3))

    def forward(self, x):
        return self.rdb3(self.rdb2(self.rdb1(x))) * 0.2 + x


class RRDBNet(nn.Module):
    def __init__(self, nf=64, nb=23, gc=32, escala=4):
        super().__init__()
        # El x2 oficial NO tiene un upsampler mas corto: tiene los mismos dos pasos de x2
        # y compensa comprimiendo la entrada con pixel_unshuffle(2), que mete los 2x2
        # vecinos en el eje de canales (3 -> 12). Por eso conv_first espera 12 canales.
        self.escala = escala
        self.conv_first = nn.Conv2d(12 if escala == 2 else 3, nf, 3, 1, 1)
        self.body = nn.Sequential(*[RRDB(nf, gc) for _ in range(nb)])
        self.conv_body = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_up1 = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_up2 = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_hr = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_last = nn.Conv2d(nf, 3, 3, 1, 1)
        self.act = nn.LeakyReLU(0.2, inplace=True)

    def forward(self, x):
        if self.escala == 2:
            x = F.pixel_unshuffle(x, 2)
        f = self.conv_first(x)
        f = f + self.conv_body(self.body(f))
        f = self.act(self.conv_up1(F.interpolate(f, scale_factor=2, mode="nearest")))
        f = self.act(self.conv_up2(F.interpolate(f, scale_factor=2, mode="nearest")))
        return self.conv_last(self.act(self.conv_hr(f)))


def cargar(ruta, escala=4, disp=None):
    disp = disp or ("mps" if torch.backends.mps.is_available() else "cpu")
    sd = torch.load(ruta, map_location="cpu", weights_only=True)
    sd = sd.get("params_ema", sd.get("params", sd))
    red = RRDBNet(escala=escala)
    red.load_state_dict(sd, strict=True)
    return red.eval().to(disp), disp
