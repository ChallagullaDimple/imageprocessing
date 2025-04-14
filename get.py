import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { PutCommand, DynamoDBDocumentClient } from "@aws-sdk/lib-dynamodb";

const client = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(client);

export const handler = async (event, context) => {
    const command = new PutCommand({
        TableName: "employee",
        Item:{
            "emailid" : event.EmailID,
            "firstname" : event.FirstName,
            "lastname" : event.LastName
            }
});

  const response = await docClient.send(command);
  console.log(response);
  return response;
};
