const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const ffmpeg = require('fluent-ffmpeg');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

console.log('Starting Video Processing Application...');
console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);

// Middleware
app.use(express.json());
app.use(express.static('public'));
app.use(cors());
console.log('Middleware configured: express.json, static, cors');

// Storage for user ratings
const allUserRatings = {};
console.log('In-memory user ratings storage initialized');

// Storage configuration for uploaded files
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = path.join(__dirname, 'uploads');
    console.log(`Storage destination requested: ${uploadDir}`);
    if (!fs.existsSync(uploadDir)) {
      console.log(`Creating upload directory: ${uploadDir}`);
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const filename = `${Date.now()}-${file.originalname}`;
    console.log(`Generated filename for upload: ${filename}`);
    cb(null, filename);
  }
});

const upload = multer({
  storage,
  fileFilter: (req, file, cb) => {
    console.log(`Received file: ${file.originalname}, mimetype: ${file.mimetype}`);
    if (file.mimetype.startsWith('video/')) {
      console.log(`Valid video file accepted: ${file.originalname}`);
      cb(null, true);
    } else {
      console.log(`Rejected non-video file: ${file.originalname}`);
      cb(new Error('Only video files are allowed!'));
    }
  },
  limits: { fileSize: 10 * 1024 * 1024 }
});
console.log('Multer configured for video uploads with 10MB limit');

// Create output directory if it doesn't exist
const outputDir = path.join(__dirname, 'processed');
if (!fs.existsSync(outputDir)) {
  console.log(`Creating output directory: ${outputDir}`);
  fs.mkdirSync(outputDir, { recursive: true });
}

// In-memory storage for activity tracking
const activityLog = [];
console.log('In-memory activity log initialized');

// Routes
app.post('/upload', (req, res) => {
  try {
    upload.single('video')(req, res, function (err) {
      if (err) {
        console.error('Multer error during upload:', err);
        return res.status(500).json({ error: 'Upload failed', details: err.message });
      }
      if (!req.file) {
        console.log('Upload failed: No file received');
        return res.status(400).json({ error: 'No video file uploaded' });
      }

      console.log(`File uploaded successfully: ${req.file.originalname} (${req.file.size} bytes)`);
      console.log(`Temporary path: ${req.file.path}`);

      const activity = {
        id: Date.now().toString(),
        originalFileName: req.file.originalname,
        uploadedFileName: req.file.filename,
        uploadPath: req.file.path,
        processedFileName: null,
        processOption: null,
        timestamp: new Date().toISOString(),
        status: 'Uploaded',
        downloadLink: null
      };

      activityLog.push(activity);
      console.log(`Activity created with ID: ${activity.id}`);
      console.log('Activity details:', activity);
      const clientActivity = {
        ...activity,
        uploadPath: undefined 
      };
      
      res.status(200).json({ activity: clientActivity });
      console.log('Upload response sent');
    });
  } catch (err) {
    console.error('Unexpected error in /upload:', err);
    res.status(500).json({ error: 'Unexpected server error', details: err.message });
  }
});

app.post('/process', (req, res) => {
  try {
    console.log('POST /process request received');
    console.log('Request body:', req.body);
    
    const { id, processOption, preset } = req.body;
    const userPreset = preset || 'podcast';
    
    if (!id || !processOption) {
      console.log('Process request missing required parameters');
      return res.status(400).json({ error: 'Missing required parameters' });
    }
    console.log(`Using preset: ${userPreset}`);

    const activity = activityLog.find(a => a.id === id);
    
    if (!activity) {
      console.log(`Activity not found with ID: ${id}`);
      return res.status(404).json({ error: 'Activity not found' });
    }

    console.log(`Processing video: ${activity.originalFileName}`);
    console.log(`Process option selected: ${processOption}`);
    
    activity.status = 'In Progress';
    activity.processOption = processOption;
    console.log(`Activity status updated to: ${activity.status}`);

    const inputPath = activity.uploadPath;
    const outputFileName = `processed-${activity.id}-${path.basename(activity.originalFileName)}`;
    let outputPath = path.join(outputDir, outputFileName);
    console.log(`Input path: ${inputPath}`);
    console.log(`Initial output path: ${outputPath}`);

    let command = ffmpeg(inputPath);
    console.log('FFmpeg command initialized');

    switch (processOption) {
      case 'mp4':
        outputPath = outputPath.replace(/\.[^/.]+$/, '.mp4');
        console.log(`Converting to MP4: ${outputPath}`);
        try {
          command.output(outputPath)
                 .format('mp4')
                 .preset(userPreset);
        } catch (err) {
          console.error('Error setting up FFmpeg output for mp4:', err);
          activity.status = 'Failed';
          return res.status(500).json({ error: 'Failed to set up FFmpeg for mp4', details: err.message });
        }
        break;
      case '720p':
        console.log(`Resizing to 720p: ${outputPath}`);
        try {
          command.output(outputPath)
                 .size('1280x720')
                 .preset(userPreset);
        } catch (err) {
          console.error('Error setting up FFmpeg output for 720p:', err);
          activity.status = 'Failed';
          return res.status(500).json({ error: 'Failed to set up FFmpeg for 720p', details: err.message });
        }
        break;
      case 'avi':
        outputPath = outputPath.replace(/\.[^/.]+$/, '.avi');
        try {
          command.output(outputPath)
                 .format('avi')
                 .videoCodec('libxvid')
                 .preset(userPreset);
        } catch (err) {
          console.error('Error setting up FFmpeg output for avi:', err);
          activity.status = 'Failed';
          return res.status(500).json({ error: 'Failed to set up FFmpeg for avi', details: err.message });
        }
        break;
      default:
        console.log(`Invalid process option: ${processOption}`);
        return res.status(400).json({ error: 'Invalid process option' });
    }

    console.log('Starting FFmpeg processing...');
    command
      .on('start', (commandLine) => {
        console.log('FFmpeg process started with command:', commandLine);
      })
      .on('progress', (progress) => {
        console.log(`Processing: ${Math.floor(progress.percent || 0)}% done`);
      })
      .on('end', () => {
        try {
          console.log(`Processing completed successfully: ${outputPath}`);
          activity.status = 'Completed';
          activity.processedFileName = path.basename(outputPath);
          activity.downloadLink = `/download/${activity.processedFileName}`;
          activity.preset = userPreset; 
          console.log(`Activity status updated to: ${activity.status}`);
          console.log('Updated activity:', activity);
          res.status(200).json({ activity });
        } catch (err) {
          console.error('Error in FFmpeg end handler:', err);
          activity.status = 'Failed';
          res.status(500).json({ error: 'Post-processing error', details: err.message });
        }
      })
      .on('error', (err) => {
        console.error('Error processing video:', err);
        console.error('Error details:', err.message);
        activity.status = 'Failed';
        console.log(`Activity status updated to: ${activity.status}`);
        
        if (!res.headersSent) {
          res.status(500).json({ error: 'Processing failed', details: err.message });
        }
      })
      .run();
    console.log('FFmpeg run command issued');
  } catch (err) {
    console.error('Unexpected error in /process:', err);
    if (!res.headersSent) {
      res.status(500).json({ error: 'Unexpected server error', details: err.message });
    }
  }
});

app.get('/download/:filename', (req, res) => {
  try {
    const filename = req.params.filename;
    console.log(`GET /download/${filename} request received`);
    
    // Validate the filename - only allow alphanumeric characters, hyphens and specific extensions
    if (!filename.match(/^[\w-]+(\.mp4|\.avi|\.mov|\.mkv)$/)) {
      console.log(`Invalid filename format: ${filename}`);
      return res.status(400).json({ error: 'Invalid filename format' });
    }
    
    // Create absolute paths for validation
    const filePath = path.join(outputDir, filename);
    const normalizedRequestPath = path.normalize(filePath);
    const normalizedOutputDir = path.normalize(outputDir);
    
    console.log(`Requested file path: ${normalizedRequestPath}`);
    console.log(`Output directory: ${normalizedOutputDir}`);
    
    // Ensure the requested file is actually within the output directory
    if (!normalizedRequestPath.startsWith(normalizedOutputDir)) {
      console.log(`Security violation: Path traversal attempt detected for: ${filename}`);
      return res.status(403).json({ error: 'Access denied' });
    }
    
    // Verify file exists
    if (!fs.existsSync(normalizedRequestPath)) {
      console.log(`File not found: ${normalizedRequestPath}`);
      return res.status(404).json({ error: 'File not found' });
    }
    
    console.log(`File download initiated: ${filename}`);
    // File is safe to download
    res.download(normalizedRequestPath, (err) => {
      if (err) {
        console.error(`Error during file download: ${err.message}`);
        if (!res.headersSent) {
          res.status(500).json({ error: 'Download failed', details: err.message });
        }
      } else {
        console.log(`File successfully downloaded: ${filename}`);
      }
    });
  } catch (err) {
    console.error('Unexpected error in /download:', err);
    if (!res.headersSent) {
      res.status(500).json({ error: 'Unexpected server error', details: err.message });
    }
  }
});

app.get('/history', (req, res) => {
  try {
    console.log('GET /history request received');
    console.log(`Current activity log has ${activityLog.length} entries`);
    res.json(activityLog);
    console.log('History response sent');
  } catch (err) {
    console.error('Unexpected error in /history:', err);
    res.status(500).json({ error: 'Unexpected server error', details: err.message });
  }
});

// New route for submitting ratings
app.post('/rate', (req, res) => {
  try {
    console.log('POST /rate request received');
    console.log('Request body:', req.body);
    
    const { userId, rating, comment } = req.body;
    
    if (!userId || !rating) {
      console.log('Rating request missing required parameters');
      return res.status(400).json({ error: 'Missing required parameters' });
    }
    
    // Initialize user's ratings object if it doesn't exist
    if (!allUserRatings[userId]) {
      allUserRatings[userId] = {};
    }
    
    // Store the rating
    allUserRatings[userId][rating] = comment || '';
    
    console.log(`Rating added for user ${userId}: ${rating} - "${comment}"`);
    console.log('Current ratings:', allUserRatings);
    
    res.status(200).json({ success: true, message: 'Rating submitted successfully' });
    console.log('Rating response sent');
  } catch (err) {
    console.error('Unexpected error in /rate:', err);
    res.status(500).json({ error: 'Unexpected server error', details: err.message });
  }
});

// Add error handling middleware
app.use((err, req, res, next) => {
  console.error('Unhandled application error:', err);
  console.error('Error stack:', err.stack);
  if (!res.headersSent) {
    res.status(500).json({ error: 'Server error', message: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`=================================================`);
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`🌐 Application URL: http://localhost:${PORT}`);
  console.log(`=================================================`);
});

console.log('Server initialization complete, waiting for connections...');

