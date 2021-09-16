package meter

import (
	"errors"
	"fmt"
	"net/http"
	"net/url"
	"strings"

	"github.com/andig/evcc/api"
	"github.com/andig/evcc/meter/lgess"
	"github.com/andig/evcc/util"
	"github.com/andig/evcc/util/request"
)

// credits to https://github.com/vloschiavo/powerwall2

// Tesla is the tesla powerwall meter
type Lgess struct {
	*request.Helper
	uri, usage string
}

func init() {
	registry.Add("lgess", NewLgessFromConfig)
}

//go:generate go run ../../cmd/tools/decorate.go -p meter -f decorateLgess -b api.Meter -o Lgess_decorators -t "api.MeterEnergy,TotalEnergy,func() (float64, error)" -t "api.Battery,SoC,func() (float64, error)"

// NewLgessFromConfig creates a Lgess Powerwall Meter from generic config
func NewLgessFromConfig(other map[string]interface{}) (api.Meter, error) {
	cc := struct {
		//URI, Usage, Password string
		URI, Usage string
	}{}

	if err := util.DecodeOther(other, &cc); err != nil {
		return nil, err
	}

	if cc.Usage == "" {
		return nil, errors.New("missing usage")
	}

	_, err := url.Parse(cc.URI)
	if err != nil {
		return nil, fmt.Errorf("%s is invalid: %s", cc.URI, err)
	}

	// support default meter names
	switch strings.ToLower(cc.Usage) {
	case "grid":
		cc.Usage = "grid"
	case "pv":
		cc.Usage = "pv"
	}

	//return NewLgess(cc.URI, cc.Usage, cc.Password)
	return NewLgess(cc.URI, cc.Usage)
}

// NewLgess creates a Lgess Meter
func NewLgess(uri, usage string) (api.Meter, error) {
	log := util.NewLogger("lgess")

	m := &Lgess{
		Helper: request.NewHelper(log),
		uri:    util.DefaultScheme(strings.TrimSuffix(uri, "/"), "https"),
		usage:  strings.ToLower(usage),
	}

	// decorate api.MeterEnergy
	var totalEnergy func() (float64, error)
	if m.usage == "load" || m.usage == "pv" {
		totalEnergy = m.totalEnergy
	}

	// decorate api.BatterySoC
	var batterySoC func() (float64, error)
	if usage == "battery" {
		batterySoC = m.batterySoC
	}

	return decorateLgess(m, totalEnergy, batterySoC), nil
}

// Login calls login and saves the returned cookie
func (m *Lgess) Login() error {
	data := map[string]interface{}{
		"username": "customer",
	}

	req, err := request.New(http.MethodPost, m.uri, request.MarshalJSON(data), request.JSONEncoding)
	if err == nil {
		// use DoBody as it will close the response body
		if _, err = m.DoBody(req); err != nil {
			err = fmt.Errorf("login failed: %w", err)
		}
	}

	return err
}

// CurrentPower implements the api.Meter interface
func (m *Lgess) CurrentPower() (float64, error) {
	var res lgess.MeterResponse
	if err := m.GetJSON(m.uri+lgess.MeterURI, &res); err != nil {
		return 0, err
	}

	if o, ok := res[m.usage]; ok {
		if m.usage == "grid" {
			return o.GridActivePower, nil
		}
		if m.usage == "pv" {
			return o.PvPower, nil
		}
		if m.usage == "battery" {
			return o.PvBatPower, nil
		}
		if m.usage == "load" {
			return o.HousePowerConsumption, nil
		}
	}

	return 0, fmt.Errorf("invalid usage: %s", m.usage)
}

// totalEnergy implements the api.MeterEnergy interface
func (m *Lgess) totalEnergy() (float64, error) {
	var res lgess.MeterResponse
	if err := m.GetJSON(m.uri+lgess.MeterURI, &res); err != nil {
		return 0, err
	}

	if o, ok := res[m.usage]; ok {
		if m.usage == "load" {
			return o.GridActiveImport, nil
		}
		if m.usage == "pv" {
			return o.GridActiveExport, nil
		}
	}

	return 0, fmt.Errorf("invalid usage: %s", m.usage)
}

// batterySoC implements the api.Battery interface
func (m *Lgess) batterySoC() (float64, error) {
	var res lgess.MeterResponse
	if err := m.GetJSON(m.uri+lgess.MeterURI, &res); err != nil {
		return 0, err
	}

	if o, ok := res[m.usage]; ok {
		return o.PvSoc, nil
	}

	return 0, fmt.Errorf("invalid usage: %s", m.usage)
}
