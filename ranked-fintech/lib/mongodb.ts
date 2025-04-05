import { MongoClient } from 'mongodb';

// Check if MongoDB URI is defined
if (!process.env.MONGODB_URI) {
  throw new Error('Please add your Mongo URI to .env.local');
}

const uri = process.env.MONGODB_URI as string;

// Define connection options that explicitly disable SSL
// This is only recommended for development environments
const options = {
  ssl: false,
  directConnection: true,
  tlsInsecure: true
};

// Global variable to hold the connection
let globalWithMongo = global as typeof globalThis & {
  _mongoClient?: MongoClient;
  _mongoClientPromise?: Promise<MongoClient>;
};

// Create or reuse a MongoDB client
export default async function connectToMongoDB() {
  try {
    // Create MongoDB client only once across hot reloads
    if (!globalWithMongo._mongoClient) {
      console.log('Creating new MongoDB client...');
      const client = new MongoClient(uri, options);
      globalWithMongo._mongoClient = client;
      
      // Connect the client
      globalWithMongo._mongoClientPromise = client.connect()
        .catch(err => {
          console.error('Failed to connect to MongoDB:', err);
          // Reset global client so we can retry connection
          globalWithMongo._mongoClient = undefined;
          globalWithMongo._mongoClientPromise = undefined;
          throw err;
        });
    }
    
    // Await the promise to get a connected client
    return await globalWithMongo._mongoClientPromise!;
  } catch (err) {
    console.error('MongoDB connection error:', err);
    throw err;
  }
} 