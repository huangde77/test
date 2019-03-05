package storage

// import (
// 	"fmt"
// 	"log"
// 	"math/rand"

// 	"go-std/src/templates"

// 	mgo "gopkg.in/mgo.v2"
// 	"gopkg.in/mgo.v2/bson"
// )

// // Mongo struct
// type Mongo struct {
// 	session *mgo.Session
// 	// collections
// 	database *mgo.Database
// 	fortunes *mgo.Collection
// 	worlds   *mgo.Collection
// }

// // Connect create connection and ping db
// func (mongo *Mongo) Connect(dbConnectionString string, maxConnectionsInPool int) error {
// 	session, err := mgo.Dial(dbConnectionString)
// 	if err != nil {
// 		log.Fatalf("Error opening database: %v", err)
// 	}

// 	mongo.database = session.DB("hello_world")
// 	mongo.worlds = mongo.database.C("world")
// 	mongo.fortunes = mongo.database.C("fortune")

// 	return nil
// }

// // Close connect to db
// func (mongo *Mongo) Close() {
// 	mongo.session.Close()
// }

// // GetOneRandomWorld return one random World struct
// func (mongo Mongo) GetOneRandomWorld() (World, error) {
// 	var w World
// 	var err error
// 	queryID := rand.Intn(worldsCount) + 1
// 	if err = mongo.worlds.Find(bson.M{"_id": queryID}).One(&w); err != nil {
// 		err = fmt.Errorf("error finding world with ID %d: %s", queryID, err)
// 	}
// 	return w, err
// }

// // UpdateRandomWorlds updates some number of worlds entries, passed as arg
// func (mongo Mongo) UpdateRandomWorlds(queries int) ([]World, error) {
// 	selectedWorlds := make([]World, queries)
// 	for i := 0; i < queries; i++ {
// 		selectedWorlds[i], _ = mongo.GetOneRandomWorld()
// 	}

// 	for _, selectedWorld := range selectedWorlds {
// 		selectedWorld.RandomNumber = rand.Intn(worldsCount) + 1
// 		if err := mongo.worlds.Update(
// 			bson.M{"_id": selectedWorld.ID},
// 			bson.M{"$set": bson.M{"randomNumber": selectedWorld.RandomNumber}},
// 		); err != nil {
// 			log.Fatalf("Error updating world with id: %s", err.Error())
// 		}
// 	}

// 	return selectedWorlds, nil
// }

// // GetFortunes finds all fortunes from table
// func (mongo Mongo) GetFortunes() ([]templates.Fortune, error) {
// 	fortunes := make([]templates.Fortune, 0, 16)

// 	if err := mongo.fortunes.Find(nil).All(&fortunes); err != nil {
// 		return nil, err
// 	}

// 	return fortunes, nil
// }

// // NewMongoDB creates new connection to mongodb with mgo driver
// func NewMongoDB(dbConnectionString string, maxConnectionsInPool int) (DB, error) {
// 	var mongo Mongo
// 	if err := mongo.Connect(dbConnectionString, maxConnectionsInPool); err != nil {
// 		return nil, err
// 	}
// 	return &mongo, nil
// }
