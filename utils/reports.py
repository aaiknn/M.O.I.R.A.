#!/usr/bin/env python3

from discord import File
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph

class Report:
  def __init__(self, **options):
    fileName = options.get('fileName')
    path = options.get('path')

    self.fileName   = fileName if fileName else 'report.pdf'
    self.filePath   = f'{path}{self.fileName}'
    self.lineHeight = 1
    self.page       = None
    self.startX     = 2*cm
    self.startY     = 26*cm

  def create(self):
    self.page = SimpleDocTemplate(
      self.filePath,
      pagesize=A4
    )

  async def send(self, ctx):
    discordFile = File(
      self.filePath,
      filename=self.fileName
    )
    await ctx.send(file=discordFile)

  def write(self, **options):
    data          = options.get('data')

    layout = getSampleStyleSheet()
    p = []
    p.append(Paragraph(
      data,
      layout['Normal']
    ))
    self.page.build(p)
