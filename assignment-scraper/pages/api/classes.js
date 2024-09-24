
import { promises as fs } from 'fs';
import path from 'path';

const CLASSES_FILE = path.join(process.cwd(), 'classes_data.json');

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { classes } = req.body;
    await fs.writeFile(CLASSES_FILE, JSON.stringify(classes));
    res.status(200).json({ message: 'Classes saved successfully.' });
  } else if (req.method === 'GET') {
    try {
      const data = await fs.readFile(CLASSES_FILE);
      const classes = JSON.parse(data);
      res.status(200).json({ classes });
    } catch (error) {
      res.status(200).json({ classes: [] });
    }
  } else {
    res.status(405).json({ message: 'Method not allowed' });
  }
}