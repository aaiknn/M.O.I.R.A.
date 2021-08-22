#!/usr/bin/env python3

from discord import File
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from typing import Dict, Tuple

class Report:
  def __init__(self, **options):
    fileName = options.get('fileName')
    path = options.get('path')

    self.fileName       = fileName if fileName else 'report.pdf'
    self.filePath       = f'{path}{self.fileName}'
    self.lineHeight     = 1
    self.page           = None
    self.spacerHeight   = 0.6*cm
    self.startX         = 2*cm
    self.startY         = 26*cm

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
    data      = options.get('data')
    layout    = getSampleStyleSheet()
    doc       = []

    for entry in data:
      if isinstance(entry, Dict):
        i     = 1
        index = 'Index'
        for item in entry['apis']:
          index += f'<br />\n{i}. {item}'
          i = i+1

        # Headline and Meta
        doc.append(Paragraph(
          entry['title'],
          layout['Heading1']
        ))
        doc.append(Paragraph(
          entry['date'],
          layout['Normal']
        ))
        doc.append(Spacer(1, self.spacerHeight))

        # Index
        doc.append(Paragraph(
          index,
          layout['Normal']
        ))
        doc.append(Spacer(2, self.spacerHeight))
        continue

      # Sub-headlines
      elif isinstance(entry, Tuple):
        doc.append(Paragraph(
          entry[0],
          layout[entry[1]]
        ))
        continue

      # Genuine paragraphs
      entry = entry.replace('\n', '<br />\n')

      doc.append(Paragraph(
        entry,
        layout['Normal']
      ))
      doc.append(Spacer(1, self.spacerHeight))

    self.page.build(doc)
