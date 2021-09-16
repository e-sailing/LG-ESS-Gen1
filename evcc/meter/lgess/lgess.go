package lgess

// credits to https://github.com/vloschiavo/powerwall2

// URIs
const (
	MeterURI = "/lgess"
)

// MeterResponse is the /api/system_status/lgess response
type MeterResponse map[string]struct {
	LastCommunicationTime string
	PvPower               float64
	PvSoc                 float64
	PvSocKW               float64
	PvBatPower            float64
	PvActivePower         float64
	HousePowerConsumption float64
	GridActivePower       float64
	GridActiveImport      float64
	GridActiveExport      float64
}

// BatteryResponse is the /api/system_status/soe response
type BatteryResponse struct {
	Percentage float64 `json:"percentage"`
}
