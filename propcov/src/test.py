import propcov as p
epoch = p.AbsoluteDate()
state = p.OrbitState()
att = p.NadirPointingAttitude()
interp = p.LagrangeInterpolator()
print(p.test(epoch, state, att, interp))
sc = p.Spacecraft(epoch, state, att, interp, 0,0,0,1,2,3)

cone_sen = p.ConicalSensor(1) 
print(cone_sen)
print(cone_sen.GetFieldOfView())

custom_sen = p.CustomSensor(p.Rvector([1,2,3]), p.Rvector([1,2,3])) 
print(custom_sen)

prop = p.Propagator(sc)
print(prop)

pg = p.PointGroup()
pg.AddUserDefinedPoints([0,1,0.5], [0,0.75,-0.45])
print(pg.GetNumPoints())


lats = [1,2,3]
lons = [1,2,3]
pg.GetLatLonVectors(lats=lats, lons=lons)
print(lats, lons)