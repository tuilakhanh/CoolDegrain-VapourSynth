from vapoursynth import core, VideoNode

# port of CoolDegrain1/2/3 as stand-alone script 

def CoolDegrain(src, tr=1, thsad=48, thsadc=None, bits=None, blksize=None, overlap=None, pel=None, recalc=False, plane=4, pf=None):
    # ensure that is clip supplied into src
    if not isinstance(src, VideoNode):
        raise TypeError('CoolDegrain: This is not a clip')

    # Vars
    if thsadc is None:
        thsadc = thsad

    if blksize is None:
        if src.width < 1280 or src.height < 720:
            blksize = 8
        elif src.width >= 3840 or src.height >= 2160:
            blksize = 32
        else:
            blksize = 16

    if overlap is None:
        overlap = blksize // 2

    if pel is None:
        if src.width < 1280 or src.height < 720:
            pel = 2
        else:
            pel = 1

    if bits is not None:
        src = core.fmtc.bitdepth(src, bits=bits)
    # Checks

    if tr not in [1, 2, 3]:
        raise ValueError('tr must be 1, 2 or 3.')

    # Stuff
 
    pfclip = pf if pf is not None else src

    super = core.mv.Super(pfclip, pel=pel, sharp=2, rfilter=4)
    
    # at least tr=1, so no checks here
    mvbw1 = core.mv.Analyse(super, isb=True, delta=1, overlap=overlap, blksize=blksize)
    mvfw1 = core.mv.Analyse(super, isb=False, delta=1, overlap=overlap, blksize=blksize)
    if tr >= 2:
        mvbw2 = core.mv.Analyse(super, isb=True, delta=2, overlap=overlap, blksize=blksize)
        mvfw2 = core.mv.Analyse(super, isb=False, delta=2, overlap=overlap, blksize=blksize)
    if tr >= 3:
        mvbw3 = core.mv.Analyse(super, isb=True, delta=3, overlap=overlap, blksize=blksize)
        mvfw3 = core.mv.Analyse(super, isb=False, delta=3, overlap=overlap, blksize=blksize)

    if recalc is True:
        hoverlap = overlap // 2
        hblksize = blksize // 2
        hthsad = thsad // 2

        prefilt = core.rgvs.RemoveGrain(src, 4)
        super_r = core.mv.Super(prefilt, pel=pel, sharp=2, rfilter=4)
        
        mvbw1 = core.mv.Recalculate(super_r, mvbw1, overlap=hoverlap, blksize=hblksize, thsad=hthsad)
        mvfw1 = core.mv.Recalculate(super_r, mvfw1, overlap=hoverlap, blksize=hblksize, thsad=hthsad)
        if tr >= 2:
            mvbw2 = core.mv.Recalculate(super_r, mvbw2, overlap=hoverlap, blksize=hblksize, thsad=hthsad)
            mvfw2 = core.mv.Recalculate(super_r, mvfw2, overlap=hoverlap, blksize=hblksize, thsad=hthsad)
        if tr >= 3:
            mvbw3 = core.mv.Recalculate(super_r, mvbw3, overlap=hoverlap, blksize=hblksize, thsad=hthsad)
            mvfw3 = core.mv.Recalculate(super_r, mvfw3, overlap=hoverlap, blksize=hblksize, thsad=hthsad)

    if tr == 1:
        filtered = core.mv.Degrain1(clip=src, super=super, mvbw=mvbw1, mvfw=mvfw1, thsad=thsad, thsadc=thsadc, plane=plane)
    elif tr == 2:
        filtered = core.mv.Degrain2(clip=src, super=super, mvbw=mvbw1, mvfw=mvfw1, mvbw2=mvbw2, mvfw2=mvfw2, thsad=thsad, thsadc=thsadc, plane=plane)
    elif tr == 3:
        filtered = core.mv.Degrain3(clip=src, super=super, mvbw=mvbw1, mvfw=mvfw1, mvbw2=mvbw2, mvfw2=mvfw2, mvbw3=mvbw3, mvfw3=mvfw3, thsad=thsad, thsadc=thsadc, plane=plane)

    return filtered
