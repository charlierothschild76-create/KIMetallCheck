import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Upload, Camera, AlertTriangle, CheckCircle, Settings, BarChart3, FileText } from 'lucide-react'
import './App.css'

function App() {
  const [inspectionResults, setInspectionResults] = useState({
    defects: [],
    measurements: null,
    status: 'ready'
  })

  const [inspectionHistory] = useState([
    { id: 1, timestamp: '2024-01-15 14:30', status: 'passed', defects: 0, part: 'Bearing Housing' },
    { id: 2, timestamp: '2024-01-15 14:25', status: 'failed', defects: 2, part: 'Gear Shaft' },
    { id: 3, timestamp: '2024-01-15 14:20', status: 'passed', defects: 0, part: 'Valve Body' },
  ])

  const handleImageUpload = () => {
    setInspectionResults({
      ...inspectionResults,
      status: 'processing'
    })
    
    // Simulate inspection process
    setTimeout(() => {
      setInspectionResults({
        defects: [
          { type: 'Kratzer', confidence: 0.92, location: 'Oberfläche links' },
          { type: 'Delle', confidence: 0.87, location: 'Zentrum' }
        ],
        measurements: {
          length: 25.4,
          width: 12.7,
          deviation: 0.1
        },
        status: 'completed'
      })
    }, 3000)
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            KI-gestützte Metallteile-Inspektion
          </h1>
          <p className="text-gray-600">
            Automatisierte Defekterkennung und Maßprüfung mit YOLOv8
          </p>
        </div>

        <Tabs defaultValue="inspection" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="inspection" className="flex items-center gap-2">
              <Camera className="w-4 h-4" />
              Inspektion
            </TabsTrigger>
            <TabsTrigger value="results" className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Ergebnisse
            </TabsTrigger>
            <TabsTrigger value="history" className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Verlauf
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Einstellungen
            </TabsTrigger>
          </TabsList>

          {/* Inspection Tab */}
          <TabsContent value="inspection" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Image Upload */}
              <Card>
                <CardHeader>
                  <CardTitle>Bild hochladen</CardTitle>
                  <CardDescription>
                    Laden Sie ein Bild des zu inspizierenden Metallteils hoch
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
                    <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 mb-4">
                      Klicken Sie hier oder ziehen Sie ein Bild hierher
                    </p>
                    <Button onClick={handleImageUpload} disabled={inspectionResults.status === 'processing'}>
                      {inspectionResults.status === 'processing' ? 'Verarbeitung...' : 'Bild auswählen'}
                    </Button>
                  </div>
                  
                  {inspectionResults.status === 'processing' && (
                    <div className="mt-4">
                      <Progress value={66} className="w-full" />
                      <p className="text-sm text-gray-600 mt-2">Analyse läuft...</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Live Camera Feed */}
              <Card>
                <CardHeader>
                  <CardTitle>Live-Kamera</CardTitle>
                  <CardDescription>
                    Echtzeitinspektion mit angeschlossener Kamera
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="bg-gray-200 rounded-lg aspect-video flex items-center justify-center">
                    <div className="text-center">
                      <Camera className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">Kamera nicht verbunden</p>
                      <Button variant="outline" className="mt-4">
                        Kamera aktivieren
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Results Tab */}
          <TabsContent value="results" className="space-y-6">
            {inspectionResults.status === 'completed' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Defect Detection Results */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5 text-orange-500" />
                      Erkannte Defekte
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {inspectionResults.defects.map((defect, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                          <div>
                            <p className="font-medium text-orange-900">{defect.type}</p>
                            <p className="text-sm text-orange-700">{defect.location}</p>
                          </div>
                          <Badge variant="outline" className="text-orange-700 border-orange-300">
                            {Math.round(defect.confidence * 100)}%
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Measurement Results */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      Maßprüfung
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Länge:</span>
                        <span className="font-medium">{inspectionResults.measurements?.length} mm</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Breite:</span>
                        <span className="font-medium">{inspectionResults.measurements?.width} mm</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Abweichung:</span>
                        <Badge variant={inspectionResults.measurements?.deviation < 0.2 ? "default" : "destructive"}>
                          ±{inspectionResults.measurements?.deviation} mm
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {inspectionResults.status === 'ready' && (
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center text-gray-500">
                    <BarChart3 className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                    <p>Keine Inspektionsergebnisse verfügbar</p>
                    <p className="text-sm">Laden Sie ein Bild hoch, um zu beginnen</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* History Tab */}
          <TabsContent value="history" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Inspektionsverlauf</CardTitle>
                <CardDescription>
                  Übersicht der letzten Inspektionen
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {inspectionHistory.map((item) => (
                    <div key={item.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center gap-4">
                        <div className={`w-3 h-3 rounded-full ${
                          item.status === 'passed' ? 'bg-green-500' : 'bg-red-500'
                        }`} />
                        <div>
                          <p className="font-medium">{item.part}</p>
                          <p className="text-sm text-gray-600">{item.timestamp}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <Badge variant={item.status === 'passed' ? "default" : "destructive"}>
                          {item.status === 'passed' ? 'Bestanden' : 'Fehlgeschlagen'}
                        </Badge>
                        <p className="text-sm text-gray-600 mt-1">
                          {item.defects} Defekte
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Konfiguration</CardTitle>
                <CardDescription>
                  Einstellungen für die Inspektionsparameter
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Erkennungsgenauigkeit</label>
                    <Progress value={85} className="mt-2" />
                    <p className="text-xs text-gray-600 mt-1">85% Mindestgenauigkeit</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Maßtoleranz</label>
                    <Progress value={20} className="mt-2" />
                    <p className="text-xs text-gray-600 mt-1">±0.2mm Toleranz</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App

