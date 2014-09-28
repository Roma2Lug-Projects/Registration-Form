# ------------------------------------------------------------------ #
# Copyright (C) 2014 Federico "MrModd" Cosentino (http://mrmodd.it/) #
# on behalf of Roma2LUG (http://lug.uniroma2.it/)                    #
# ------------------------------------------------------------------ #

from django.shortcuts import render
from django.http import HttpResponse
import qrcode
import qrcode.image.svg
from qrcode.image.pure import PymagingImage

# Create your views here.
def qrview(request, qr_id):
	return render(request, 'simple_qrcode/show.html', {'qr_id': qr_id})

def qrsvg(request, qr_id):
	factory = qrcode.image.svg.SvgImage
	img = qrcode.make(qr_id, image_factory=factory)
	response = HttpResponse(content_type="image/svg+xml")
	img.save(response, "SVG")
	return response

def qrpng(request, qr_id):
	img = qrcode.make(qr_id, image_factory=PymagingImage)
	response = HttpResponse(content_type="image/png")
	img.save(response, "PNG")
	return response
