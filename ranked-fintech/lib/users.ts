import connectToMongoDB from './mongodb';
import { ObjectId } from 'mongodb';

// User type definition
export interface User {
  _id?: ObjectId;
  auth0Id: string;
  email: string;
  name?: string;
  picture?: string;
  elo: number;  // ELO rating is kept as a read-only field
  isAdmin?: boolean;
  createdAt: Date;
  updatedAt: Date;
  lastLogin: Date;
}

// Create a new user or update if exists, but preserves the ELO value
export async function createOrUpdateUser(userData: Partial<User>): Promise<User> {
  try {
    // Connect to the database
    const client = await connectToMongoDB();
    const db = client.db(process.env.MONGODB_DB || 'rankedfintech');
    const users = db.collection<User>('users');

    const now = new Date();
    
    // Check if user already exists
    const existingUser = userData.auth0Id 
      ? await users.findOne({ auth0Id: userData.auth0Id }) 
      : null;

    if (existingUser) {
      // Update existing user but preserve the ELO rating
      const updatedUser = {
        ...existingUser,
        ...userData,
        // Keep the existing ELO rating - don't overwrite it
        elo: existingUser.elo,
        updatedAt: now,
        lastLogin: now
      };
      
      await users.updateOne(
        { auth0Id: userData.auth0Id },
        { $set: updatedUser }
      );
      
      return updatedUser;
    } else {
      // Create new user with default ELO
      const newUser = {
        ...userData,
        // Set initial ELO rating (1000 is typical)
        elo: 1000,
        createdAt: now,
        updatedAt: now,
        lastLogin: now
      } as User;
      
      const result = await users.insertOne(newUser);
      return { ...newUser, _id: result.insertedId };
    }
  } catch (error) {
    console.error('Error in createOrUpdateUser:', error);
    throw error;
  }
}

// Get user by Auth0 ID
export async function getUserByAuth0Id(auth0Id: string): Promise<User | null> {
  try {
    const client = await connectToMongoDB();
    const db = client.db(process.env.MONGODB_DB || 'rankedfintech');
    
    return db.collection<User>('users').findOne({ auth0Id });
  } catch (error) {
    console.error('Error in getUserByAuth0Id:', error);
    throw error;
  }
}

// Get user by ID
export async function getUserById(id: string): Promise<User | null> {
  try {
    const client = await connectToMongoDB();
    const db = client.db(process.env.MONGODB_DB || 'rankedfintech');
    
    return db.collection<User>('users').findOne({ _id: new ObjectId(id) });
  } catch (error) {
    console.error('Error in getUserById:', error);
    throw error;
  }
} 