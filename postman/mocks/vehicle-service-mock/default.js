const http = require("http");

const server = http.createServer((req, res) => {
  const method = req.method;
  const urlObj = new URL(req.url, `http://localhost`);
  const pathname = urlObj.pathname;

  // @endpoint GET /vehicles
  if (method === "GET" && pathname === "/vehicles") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify([
      {
        "id": 1,
        "nickName": "The Lisa Marie",
        "vin": "4M2DV11W4RDJ53329",
        "make": "Mercury",
        "model": "Villager",
        "year": "1994",
        "miles": 159864
      },
      {
        "id": 2,
        "nickName": "Dolly",
        "vin": "JN8AZ2KR1AT169594",
        "make": "Nissan",
        "model": "Cube",
        "year": "2010",
        "miles": 59000
      }
    ]));
    return;
  }

  // @endpoint POST /vehicles
  if (method === "POST" && pathname === "/vehicles") {
    let body = "";
    req.on("data", chunk => { body += chunk; });
    req.on("end", () => {
      let parsed = {};
      try { parsed = JSON.parse(body); } catch (e) {}
      // If vin is missing, return 400
      if (!parsed.vin) {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ "message": "Request body missing required attribute: vin" }));
        return;
      }
      res.writeHead(201, { "Content-Type": "application/json" });
      res.end(JSON.stringify({
        "id": 1,
        "nickName": parsed.nickName || "The Lisa Marie",
        "vin": parsed.vin || "4M2DV11W4RDJ53329",
        "make": parsed.make || "Mercury",
        "model": parsed.model || "Villager",
        "year": parsed.year || "1994",
        "miles": "159,864"
      }));
    });
    return;
  }

  // @endpoint GET /vehicles/:id
  if (method === "GET" && /^\/vehicles\/[^/]+$/.test(pathname)) {
    const id = pathname.split("/")[2];
    if (id === "0") {
      res.writeHead(404, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ "message": `Vehicle with id: ${id} not found.` }));
      return;
    }
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({
      "id": parseInt(id) || 1,
      "nickName": "The Lisa Marie",
      "vin": "4M2DV11W4RDJ53329",
      "make": "Mercury",
      "model": "Villager",
      "year": "1994",
      "miles": 159864
    }));
    return;
  }

  // @endpoint PATCH /vehicles/:id
  if (method === "PATCH" && /^\/vehicles\/[^/]+$/.test(pathname)) {
    const id = pathname.split("/")[2];
    let body = "";
    req.on("data", chunk => { body += chunk; });
    req.on("end", () => {
      let parsed = {};
      try { parsed = JSON.parse(body); } catch (e) {}
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({
        "id": parseInt(id) || 1,
        "nickName": parsed.nickName || "The Lisa Marie",
        "vin": parsed.vin || "4M2DV11W4RDJ53329",
        "make": parsed.make || "Mercury",
        "model": parsed.model || "Villager",
        "year": parsed.year || "1994",
        "miles": parsed.miles || 159999
      }));
    });
    return;
  }

  // @endpoint DELETE /vehicles/:id
  if (method === "DELETE" && /^\/vehicles\/[^/]+$/.test(pathname)) {
    res.writeHead(204, {});
    res.end("");
    return;
  }

  // 404 fallback
  res.writeHead(404, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ "message": "Route not found." }));
});

server.listen(process.env.PORT || 4500);
