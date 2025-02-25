```mermaid
graph TD
  subgraph Cloud
    DjangoServer["🌐 Cloud-Based Django Server"]
  end

  subgraph Remote_Weather_Stations
    RemoteStation1["🌡️ Remote Weather Station 1"]
    RemoteStation2["🌡️ Remote Weather Station 2"]
  end

  subgraph Local_Network
    HandyDevice["📱 Device (Handy)"]
    LocalWeatherStation["🌦️ Local Weather Station"]
  end

  %% Data Flow %%
  RemoteStation1 -- "PUT: Upload Data" --> DjangoServer
  RemoteStation2 -- "PUT: Upload Data" --> DjangoServer
  LocalWeatherStation -- "PUT: Upload Data" --> DjangoServer
  DjangoServer -- "GET: Config/Commands" --> RemoteStation1
  DjangoServer -- "GET: Config/Commands" --> RemoteStation2
  DjangoServer -- "GET: Config/Commands" --> LocalWeatherStation
  HandyDevice -- "GET: Fetch Reports/Data" --> DjangoServer
  HandyDevice -- "GET: Direct Query" --> LocalWeatherStation
```