# Copyright (C) 2015 Associated Universities, Inc. Washington DC, USA.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# 
# Correspondence concerning GBT software should be addressed as follows:
#       GBT Operations
#       National Radio Astronomy Observatory
#       P. O. Box 2
#       Green Bank, WV 24944-0002 USA

import pyfits
import time

def make_header(xctr, yctr, xsize, ysize, pix_scale, coordType, radesys, equinox, restfreq, faxis, beam_fwhm, veldef, specsys, proj="SFL"):

    hdr = pyfits.Header()

    # BASIC stuff, the WCS code needs this
    hdr['NAXIS'] = 4
    hdr['NAXIS1'] = xsize
    hdr['NAXIS2'] = ysize
    hdr['NAXIS3'] = len(faxis)
    hdr['NAXIS4'] = 1

    ctypeDashes = '----'

    xctype = coordType[0] + ctypeDashes[len(coordType[0]):]
    yctype = coordType[1] + ctypeDashes[len(coordType[1]):]

    # MAKE THE POSITION AXES
    if proj == 'TAN':
        hdr['CTYPE1'] = xctype + '-TAN'
        hdr['CRVAL1'] = xctr
        hdr['CRPIX1'] = (xsize/2.0)
        hdr['CDELT1'] = -1.0*pix_scale

        hdr['CTYPE2'] = yctype + '-TAN'
        hdr['CRVAL2'] = yctr
        hdr['CRPIX2'] = (ysize/2.)
        hdr['CDELT2'] = pix_scale
    elif proj == 'SFL':
        hdr['CTYPE1'] = xctype + '-SFL'
        hdr['CRVAL1'] = xctr
        hdr['CRPIX1'] = (xsize/2.)
        hdr['CDELT1'] = -1.0*pix_scale

        # GLS projection always has CRVAL2 at 0.0
        # set CRPIX2 so that at the center pixel (ysize/2)
        # the y value is yctr
        hdr['CTYPE2'] = yctype + '-SFL'
        hdr['CRVAL2'] = 0.0
        yctrPix = (ysize/2.0) + 1.0
        hdr['CRPIX2'] = yctrPix - (yctr/pix_scale)
        hdr['CDELT2'] = pix_scale
    else:
        raise Exception("%s is an invalid projection code, must be one of 'TAN' or 'SFL'" % proj)        

    # MAKE THE VELOCITY AXIS (ALONG THE THIRD DIMENSION)
    # the frame is now indicated via SPECSYS.  Check on any other
    # needed WCS keywords for use here.
    hdr['CTYPE3'] = 'FREQ'
    hdr['CUNIT3'] = 'Hz'
    hdr['CRVAL3'] = faxis[0]
    hdr['CRPIX3'] = 1.0
    hdr['CDELT3'] = faxis[1]-faxis[0]

    # STOKES axis - always I
    hdr['CTYPE4'] = 'STOKES'
    hdr['CRVAL4'] = 1.0
    hdr['CRPIX4'] = 1.0
    hdr['CDELT4'] = 1.0

    hdr['SPECSYS'] = specsys

    # AIPS velocity type
    hdr['VELREF'] = 0
    if specsys == "LSRK":
        hdr['VELREF'] = 1
    elif specsys == "HELIOCEN":
        hdr['VELREF'] = 2
    elif specsys == "TOPOCENT":
        hdr['VELREF'] = 3
    # no others are defined in the original AIPS memo, should search for updates
    # for now, leave everything else at 0
    if veldef == "RADI":
        # radio definition adds 256
        hdr['VELREF'] = hdr['VELREF'] + 256
    # AIPS memo doesn't say what to do for relativistic velocity definition

    # Set the ALT* axis keywords if possible
    if hdr['CDELT3'] != 0. and restfreq > 0.:
        # zero velocity
        hdr['ALTRVAL'] = 0.0
        # is at channel here the frequency axis equals the rest frequency
        hdr['ALTRPIX'] = hdr['CRPIX3'] + (restfreq - hdr['CRVAL3'])/hdr['CDELT3']
        
    hdr['RESTFRQ'] = restfreq

    # ADD THE RADESYS and EQUINOX when appropriate
    if radesys is not None and len(radesys) > 0:
        hdr['RADESYS'] = radesys
    if equinox is not None and equinox > 0.0:
        hdr['EQUINOX'] = equinox

    return hdr
