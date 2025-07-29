import React, { useState } from 'react';
import {
  Container,
  Typography,
  Button,
  Box,
  Table,
  TableBody,
  TableCell,
  TableRow,
  TableHead,
  Paper,
  CircularProgress
} from '@mui/material';

const API_URL = process.env.REACT_APP_API_URL;

function cleanRows(rows) {
  return rows
    .filter(row => row.length > 1 && row.some(cell => cell.trim() !== ''))
    .map(row => {
      const filtered = row.filter(cell => cell && cell.trim() !== '');
      return filtered;
    });
}

function App() {
  const [tables, setTables] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filename, setFilename] = useState('');

  const handleFileChange = (e) => {
    setFilename(e.target.files[0]?.name || '');
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('pdf-upload');
    if (!fileInput.files.length) return;

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    setLoading(true);
    setTables([]);

    try {
      const res = await fetch(process.env.REACT_APP_API_URL + "/extract", {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.tables) {
        const cleaned = data.tables.map(table => ({
          page: table.page,
          rows: cleanRows(table.rows)
        }));
        setTables(cleaned);
      }
    } catch (err) {
      console.error('Error uploading PDF:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 6 }}>
      <Typography variant="h4" gutterBottom>
        PDF Table Extractor
      </Typography>

      <Box component="form" onSubmit={handleUpload} sx={{ mb: 4 }}>
        <input
          id="pdf-upload"
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
          hidden
        />
        <label htmlFor="pdf-upload">
          <Button variant="outlined" component="span">
            Choose PDF
          </Button>
        </label>
        {filename && <Typography variant="body2" sx={{ ml: 2, display: 'inline' }}>{filename}</Typography>}
        <Button type="submit" variant="contained" sx={{ ml: 2 }}>
          Upload & Extract
        </Button>
      </Box>

      {loading && <CircularProgress />}

      {tables.map((table, i) => (
        <Box key={i} component={Paper} sx={{ mb: 4, p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Page {table.page}
          </Typography>
          <Table size="small">
            <TableHead>
              <TableRow>
                {table.rows[0]?.map((cell, idx) => (
                  <TableCell key={idx}><strong>{cell}</strong></TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {table.rows.slice(1).map((row, rIdx) => (
                <TableRow key={rIdx}>
                  {row.map((cell, cIdx) => (
                    <TableCell key={cIdx}>{cell}</TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>
      ))}
    </Container>
  );
}

export default App;
