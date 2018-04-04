# Celery AutoScale

Celery Autoscale is a service powered by AWS Lambda that runs every minute and 
collect total pending task from broker (Redis or RabbitMQ) put the metric(pendingTask) on Cloudwatch. These celery inspect support redis and rabbitMQ broker.

This metric can be used for following purpose:
- To trigger scale up and scale down activity for celery worker autoscaling group.
- To trigger alarm mails if pendingtask count goes too high.

## Supported broker

- Redis
    - It connects to redis and poll queue stats. So, you have to allow aws lambda to make redis connection.
- RabbitMQ
    - It uses rabbitmq_management plugin http api to query stats. So, You have to enable rabbitmq_management plugin with this [rabbitmq help](https://www.rabbitmq.com/management.html#getting-started).


## Update celery info in serverless

```functions:
  CeleryCloudWatch:
    handler: handler.celery_task_status_watch_handler
    description: Collects celery peding task count to celery cloudwatch
    events:
      - schedule:
          rate: rate(1 minute)
          enabled: true
          input:
            service: test
            broker: redis://localhost:6379/0
            queues: ["celery"]
```

CeleryCloudWatch Function need 3 inputs 
 
   input   | description 
   ------- | :----------
   service | custom cloud watch dimension service name 
   broker  | broker url. Sample( Redis: redis://localhost:6379/0 , RabbitMQ: amqp://myuser:mypassword@localhost:5672/myvhost)
   queues  | Array of queues whose pending task count will be calculated




## Installation 
- [serverless](https://serverless.com)
- python3.6

    We are using serverless for lambda setup on AWS. To deploy run this command 
    
    ```./deploy.sh <stage> [aws profile]``` stage can be dev or staging
    

## Additional

 You can use [serverless-plugin-aws-alerts](https://serverless.com/blog/serverless-ops-metrics/)
  plugin to create cloud watch alerts on `pendingTask` metrics.
  
  Let's say I want an email alert whenever I see more than 1000 pending task in 5 minutes:
    
    
      # serverless.yml

        plugins:
          - serverless-plugin-aws-alerts
        
        custom:
          alerts:
            stages:
              - producton
            topics:
              alarm: 
                topic: ${self:service}-${opt:stage}-alerts-alarm
                notifications:
                  - protocol: email
                    endpoint: name@domain.com
            definitions:
              tooManyTasksAlarm:
                description: 'Pending Task Overflow'
                namespace: 'Celery/Queue'
                metric: pendingTask
                threshold: 1000
                statistic: Sum
                period: 600
                evaluationPeriods: 1
                comparisonOperator: GreaterThanOrEqualToThreshold
            alarms:
              - tooManyTasksAlarm

## License

GNU General Public License v3.0 (see [LICENSE](LICENSE))
