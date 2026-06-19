# panchanga.py -- routines for computing tithi, vara, etc.
#
# Copyright (C) 2013 Satish BD
# Downloaded from https://github.com/bdsatish/drik-panchanga
#
# Vendored from the drik-panchanga project, with minimal modifications:
#   - ephe path now reads from SE_EPHE_PATH env var, falling back to default
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""Use Swiss ephemeris to calculate tithi, nakshatra, etc."""

from __future__ import division
from math import ceil
from collections import namedtuple as struct
import os
import swisseph as swe

coordinate_flag = swe.FLG_SIDEREAL
nakshatra_system = 'equal'
chosen_ayanamsa = 'Lahiri'

Date = struct('Date', ['year', 'month', 'day'])
Place = struct('Place', ['latitude', 'longitude', 'timezone'])

sidereal_year = 365.256360417

_rise_flags = swe.BIT_DISC_CENTER + swe.BIT_NO_REFRACTION

swe.RAHU = swe.MEAN_NODE
swe.KETU = swe.PLUTO
planet_list = [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER,
               swe.VENUS, swe.SATURN, swe.MEAN_NODE,
               swe.KETU, swe.URANUS, swe.NEPTUNE]

def set_coordinate_mode(mode='sidereal'):
    global coordinate_flag
    if mode.lower() == 'sidereal':
        coordinate_flag = swe.FLG_SIDEREAL
    elif mode.lower() == 'tropical':
        coordinate_flag = swe.FLG_TROPICAL
    else:
        coordinate_flag = swe.FLG_SIDEREAL
        print('Unknown coordinate mode. Assuming sidereal.')

def set_nakshatra_system(system='classical'):
    global nakshatra_system
    if system.lower() in ['classical', 'equal']:
        nakshatra_system = 'equal'
    elif system.lower() in ['garga', 'unequal']:
        nakshatra_system = 'unequal'
    else:
        nakshatra_system = 'equal'
        print('Unknown nakshatra system mode. Assuming classical equal spacing.')

def set_chosen_ayanamsa(ayanamsa='lahiri'):
    global chosen_ayanamsa
    chosen_ayanamsa = ayanamsa.lower()

def set_ayanamsa_mode():
    ayanamsa = chosen_ayanamsa.lower()
    if ayanamsa == 'citra':
        swe.set_sid_mode(swe.SIDM_TRUE_CITRA)
    elif ayanamsa == 'revati':
        swe.set_sid_mode(swe.SIDM_TRUE_REVATI)
    elif ayanamsa == 'pushya':
        swe.set_sid_mode(swe.SIDM_TRUE_PUSHYA)
    elif ayanamsa == 'mula':
        swe.set_sid_mode(swe.SIDM_TRUE_MULA)
    elif ayanamsa == 'rohini':
        swe.set_sid_mode(swe.SIDM_USER, 1845436.103611175, 0)
    elif ayanamsa == 'rohini_garga':
        swe.set_sid_mode(swe.SIDM_USER, 1757748.5933482398, 0)
    elif ayanamsa == 'lahiri':
        swe.set_sid_mode(swe.SIDM_LAHIRI)
    elif ayanamsa == 'krishnamurti':
        swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
    elif ayanamsa == 'raman':
        swe.set_sid_mode(swe.SIDM_RAMAN)
    elif ayanamsa == 'usha_shashi' or ayanamsa == 'ushashashi':
        swe.set_sid_mode(swe.SIDM_USHASHASHI)
    elif ayanamsa == 'suryasiddhanta':
        swe.set_sid_mode(swe.SIDM_SURYASIDDHANTA)
    elif ayanamsa == 'revati_359_50':
        swe.set_sid_mode(swe.SIDM_USER, 1926892.343164331, 0)
    elif ayanamsa == 'galc_cent_mid_mula':
        swe.set_sid_mode(swe.SIDM_USER, 1922011.128853056, 0)
    else:
        swe.set_sid_mode(swe.SIDM_FAGAN_BRADLEY)

reset_ayanamsa_mode = lambda: swe.set_sid_mode(swe.SIDM_FAGAN_BRADLEY)

garga_end_points = [degs + mins / 60 for degs, mins in [
    (0, 0), (13, 20), (20, 0), (33, 20), (53, 20), (66, 40), (73, 20), (93, 20),
    (106, 40), (113, 20), (126, 40), (140, 0), (160, 0), (173, 20), (186, 40),
    (193, 20), (213, 20), (226, 40), (233, 20), (246, 40), (260, 0), (280, 0),
    (293, 20), (306, 40), (312, 20), (326, 40), (346, 40), (360, 0)]]

def get_planet_name(planet):
    names = {swe.SUN: 'Surya', swe.MOON: 'Candra', swe.KUJA: 'Mangala',
             swe.MERCURY: 'Budha', swe.JUPITER: 'Guru', swe.VENUS: 'Sukra',
             swe.SATURN: 'Sani', swe.RAHU: 'Rahu', swe.KETU: 'Ketu', swe.PLUTO: 'Ketu'}
    return names[planet]

from_dms = lambda degs, mins, secs=0: degs + mins / 60 + secs / 3600

def to_dms_prec(deg):
    d = int(deg)
    mins = (deg - d) * 60
    m = int(mins)
    s = round((mins - m) * 60, 6)
    return [d, m, s]

def to_dms(deg):
    d, m, s = to_dms_prec(deg)
    return [d, m, int(s)]

def unwrap_angles(angles):
    result = angles
    for i in range(1, len(angles)):
        if result[i] < result[i - 1]:
            result[i] += 360
    assert (result == sorted(result))
    return result

norm180 = lambda angle: (angle - 360) if angle >= 180 else angle
norm360 = lambda angle: angle % 360
ketu = lambda rahu: (rahu + 180) % 360

# Use SE_EPHE_PATH environment variable if set, otherwise default path.
_ephe_path = os.environ.get("SE_EPHE_PATH")
if _ephe_path:
    swe.set_ephe_path(_ephe_path)
init_swisseph = lambda: None

def function(point):
    swe.set_sid_mode(swe.SIDM_USER, point, 0.0)
    fval = swe.fixstar_ut("Citra", point, flags=swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0] - 180
    return fval

def bisection_search(func, start, stop):
    left = start
    right = stop
    epsilon = 5E-10
    while True:
        middle = (left + right) / 2
        midval = func(middle)
        rtval = func(right)
        if midval * rtval >= 0:
            right = middle
        else:
            left = middle
        if (right - left) <= epsilon:
            break
    found = (right + left) / 2
    fval = func(found)
    if round(fval, 6) != 0:
        print(f"{func.__name__}({found}) = {fval} != 0")
        print("WARNING: convergence likely failed; answer is unreliable.")
    return found

def inverse_lagrange(x, y, ya):
    assert (len(x) == len(y))
    total = 0
    for i in range(len(x)):
        numer = 1
        denom = 1
        for j in range(len(x)):
            if j != i:
                numer *= (ya - y[j])
                denom *= (y[i] - y[j])
        total += numer * x[i] / denom
    return total

gregorian_to_jd = lambda date, hours=0.0: swe.julday(date.year, date.month, date.day, hours)
jd_to_gregorian = lambda jd: swe.revjul(jd, swe.GREG_CAL)

def local_time_to_jdut1(year, month, day, hour=0, minutes=0, seconds=0, timezone=0.0):
    y, m, d, h, mnt, s = swe.utc_time_zone(year, month, day, hour, minutes, seconds, timezone)
    jd_et, jd_ut1 = swe.utc_to_jd(y, m, d, h, mnt, 0, cal=swe.GREG_CAL)
    return jd_ut1

def nakshatra_end_point(nakshatra_number):
    if nakshatra_system == 'unequal':
        return garga_end_points[nakshatra_number]
    else:
        return nakshatra_number * 360 / 27

def nakshatra_pada(longitude):
    if nakshatra_system == 'unequal':
        return nakshatra_pada_unequal_system(longitude)
    else:
        return nakshatra_pada_equal_spacing(longitude)

def nakshatra_pada_equal_spacing(longitude):
    one_star = (360 / 27)
    one_pada = (360 / 108)
    quotient = int(longitude / one_star)
    reminder = (longitude - quotient * one_star)
    pada = int(reminder / one_pada)
    return [1 + quotient, 1 + pada]

def nakshatra_pada_unequal_system(longitude):
    assert (longitude > 0)
    assert (longitude < 360)
    end_points = garga_end_points
    for nak in range(len(end_points)):
        if longitude < end_points[nak]:
            break
    one_pada = (end_points[nak] - end_points[nak - 1]) / 4
    for pada in [1, 2, 3, 4]:
        if longitude < end_points[nak - 1] + pada * one_pada:
            break
    return [nak, pada]

def planet_longitude(jd, planet):
    set_ayanamsa_mode()
    longi = swe.calc_ut(jd, planet, flags=swe.FLG_SWIEPH | coordinate_flag)
    reset_ayanamsa_mode()
    return norm360(longi[0][0])

solar_longitude = lambda jd: planet_longitude(jd, swe.SUN)
lunar_longitude = lambda jd: planet_longitude(jd, swe.MOON)

def sunrise(jd, place):
    lat, lon, tz = place
    result = swe.rise_trans(jd - tz / 24, swe.SUN, geopos=(lon, lat, 0), rsmi=_rise_flags + swe.CALC_RISE)
    rise = result[1][0]
    return [rise + tz / 24., to_dms((rise - jd) * 24 + tz)]

def sunset(jd, place):
    lat, lon, tz = place
    result = swe.rise_trans(jd - tz / 24, swe.SUN, geopos=(lon, lat, 0), rsmi=_rise_flags + swe.CALC_SET)
    setting = result[1][0]
    return [setting + tz / 24., to_dms((setting - jd) * 24 + tz)]

def moonrise(jd, place):
    lat, lon, tz = place
    result = swe.rise_trans(jd - tz / 24, swe.MOON, geopos=(lon, lat, 0), rsmi=_rise_flags + swe.CALC_RISE)
    rise = result[1][0]
    return to_dms((rise - jd) * 24 + tz)

def moonset(jd, place):
    lat, lon, tz = place
    result = swe.rise_trans(jd - tz / 24, swe.MOON, geopos=(lon, lat, 0), rsmi=_rise_flags + swe.CALC_SET)
    setting = result[1][0]
    return to_dms((setting - jd) * 24 + tz)

def tithi(jd, place):
    tz = place.timezone
    rise = sunrise(jd, place)[0] - tz / 24
    moon_phase = lunar_phase(rise)
    today = ceil(moon_phase / 12)
    degrees_left = today * 12 - moon_phase
    offsets = [0.25, 0.5, 0.75, 1.0]
    lunar_long_diff = [(lunar_longitude(rise + t) - lunar_longitude(rise)) % 360 for t in offsets]
    solar_long_diff = [(solar_longitude(rise + t) - solar_longitude(rise)) % 360 for t in offsets]
    relative_motion = [moon - sun for (moon, sun) in zip(lunar_long_diff, solar_long_diff)]
    y = relative_motion
    x = offsets
    approx_end = inverse_lagrange(x, y, degrees_left)
    ends = (rise + approx_end - jd) * 24 + tz
    answer = [int(today), to_dms(ends)]
    moon_phase_tmrw = lunar_phase(rise + 1)
    tomorrow = ceil(moon_phase_tmrw / 12)
    isSkipped = (tomorrow - today) % 30 > 1
    if isSkipped:
        leap_tithi = today + 1
        degrees_left = leap_tithi * 12 - moon_phase
        approx_end = inverse_lagrange(x, y, degrees_left)
        ends = (rise + approx_end - jd) * 24 + place.timezone
        leap_tithi = 1 if today == 30 else leap_tithi
        answer += [int(leap_tithi), to_dms(ends)]
    return answer

def nakshatra(jd, place):
    lat, lon, tz = place
    rise = sunrise(jd, place)[0] - tz / 24.
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    longitudes = [lunar_longitude(rise + t) for t in offsets]
    nak = nakshatra_pada(longitudes[0])[0]
    y = unwrap_angles(longitudes)
    x = offsets
    approx_end = inverse_lagrange(x, y, nakshatra_end_point(nak))
    ends = (rise - jd + approx_end) * 24 + tz
    answer = [int(nak), to_dms(ends)]
    nak_tmrw = nakshatra_pada(longitudes[-1])[0]
    isSkipped = (nak_tmrw - nak) % 27 > 1
    if isSkipped:
        leap_nak = nak + 1
        approx_end = inverse_lagrange(offsets, longitudes, nakshatra_end_point(leap_nak))
        ends = (rise - jd + approx_end) * 24 + tz
        leap_nak = 1 if nak == 27 else leap_nak
        answer += [int(leap_nak), to_dms(ends)]
    return answer

def yoga(jd, place):
    lat, lon, tz = place
    rise = sunrise(jd, place)[0] - tz / 24.
    lunar_long = lunar_longitude(rise)
    solar_long = solar_longitude(rise)
    total = (lunar_long + solar_long) % 360
    yog = ceil(total * 27 / 360)
    degrees_left = yog * (360 / 27) - total
    offsets = [0.25, 0.5, 0.75, 1.0]
    lunar_long_diff = [(lunar_longitude(rise + t) - lunar_longitude(rise)) % 360 for t in offsets]
    solar_long_diff = [(solar_longitude(rise + t) - solar_longitude(rise)) % 360 for t in offsets]
    total_motion = [moon + sun for (moon, sun) in zip(lunar_long_diff, solar_long_diff)]
    y = total_motion
    x = offsets
    approx_end = inverse_lagrange(x, y, degrees_left)
    ends = (rise + approx_end - jd) * 24 + tz
    answer = [int(yog), to_dms(ends)]
    lunar_long_tmrw = lunar_longitude(rise + 1)
    solar_long_tmrw = solar_longitude(rise + 1)
    total_tmrw = (lunar_long_tmrw + solar_long_tmrw) % 360
    tomorrow = ceil(total_tmrw * 27 / 360)
    isSkipped = (tomorrow - yog) % 27 > 1
    if isSkipped:
        leap_yog = yog + 1
        degrees_left = leap_yog * (360 / 27) - total
        approx_end = inverse_lagrange(x, y, degrees_left)
        ends = (rise + approx_end - jd) * 24 + tz
        leap_yog = 1 if yog == 27 else leap_yog
        answer += [int(leap_yog), to_dms(ends)]
    return answer

def karana(jd, place):
    tz = place.timezone
    rise = sunrise(jd, place)[0]
    moon_phase = lunar_phase(rise)
    today = ceil(moon_phase / 6)
    degrees_left = today * 6 - moon_phase
    offsets = [0.25, 0.5, 0.75, 1.0]
    lunar_long_diff = [(lunar_longitude(rise + t) - lunar_longitude(rise)) % 360 for t in offsets]
    solar_long_diff = [(solar_longitude(rise + t) - solar_longitude(rise)) % 360 for t in offsets]
    relative_motion = [moon - sun for (moon, sun) in zip(lunar_long_diff, solar_long_diff)]
    y = relative_motion
    x = offsets
    approx_end = inverse_lagrange(x, y, degrees_left)
    ends = (rise + approx_end - jd) * 24 + tz
    answer = [int(today), to_dms(ends)]
    return answer

def vaara(jd):
    return int(ceil(jd + 1) % 7)

def masa(jd, place, amanta=True):
    ti = tithi(jd, place)[0]
    critical = sunrise(jd, place)[0]
    last_moon = new_moon(critical, ti, -1) if amanta else full_moon(critical, ti, -1)
    next_moon = new_moon(critical, ti, +1) if amanta else full_moon(critical, ti, +1)
    this_solar_month = raasi(last_moon)
    next_solar_month = raasi(next_moon)
    is_leap_month = (this_solar_month == next_solar_month)
    if amanta:
        maasa = this_solar_month + 1
    else:
        maasa = 1 if (this_solar_month == 10 and ti >= 15) else this_solar_month + 2
    if maasa > 12:
        maasa = (maasa % 12)
    return [int(maasa), is_leap_month]

ahargana = lambda jd: jd - 588465.5

def elapsed_year(jd, maasa_num):
    ahar = ahargana(jd)
    kali = int((ahar + (4 - maasa_num) * 30) / sidereal_year)
    saka = kali - 3179
    vikrama = saka + 135
    return kali, saka

def new_moon(jd, tithi_, opt=-1):
    if opt == -1:
        start = jd - tithi_
    if opt == +1:
        start = jd + (30 - tithi_)
    x = [-2 + offset / 4 for offset in range(17)]
    y = [lunar_phase(start + i) for i in x]
    y = unwrap_angles(y)
    y0 = inverse_lagrange(x, y, 360)
    return start + y0

def full_moon(jd, tithi_, opt=-1):
    if opt == -1:
        start = jd - (tithi_ - 15) if tithi_ > 15 else jd - (tithi_ + 15)
    if opt == +1:
        start = jd + (15 - tithi_) if tithi_ < 15 else jd - tithi_ + 45
    x = [-2 + offset / 4 for offset in range(17)]
    y = [lunar_phase(start + i) for i in x]
    y = unwrap_angles(y)
    y0 = inverse_lagrange(x, y, 180)
    return start + y0

def raasi(jd):
    solar_nirayana = solar_longitude(jd)
    return ceil(solar_nirayana / 30.)

def lunar_phase(jd):
    solar_long = solar_longitude(jd)
    lunar_long = lunar_longitude(jd)
    moon_phase = (lunar_long - solar_long) % 360
    return moon_phase

def samvatsara(jd, maasa_num):
    kali = elapsed_year(jd, maasa_num)[0]
    if kali >= 4009:
        kali = (kali - 14) % 60
    samvat = (kali + 27 + int((kali * 211 - 108) / 18000)) % 60
    return samvat

def ritu(masa_num):
    return (masa_num - 1) // 2

def day_duration(jd, place):
    srise = sunrise(jd, place)[0]
    sset = sunset(jd, place)[0]
    diff = (sset - srise) * 24
    return [diff, to_dms(diff)]

def gauri_chogadiya(jd, place):
    lat, lon, tz = place
    tz = place.timezone
    srise = swe.rise_trans(jd - tz / 24, swe.SUN, geopos=(lon, lat, 0), rsmi=_rise_flags + swe.CALC_RISE)[1][0]
    sset = swe.rise_trans(jd - tz / 24, swe.SUN, geopos=(lon, lat, 0), rsmi=_rise_flags + swe.CALC_SET)[1][0]
    day_dur = (sset - srise)
    end_times = []
    for i in range(1, 9):
        end_times.append(to_dms((srise + (i * day_dur) / 8 - jd) * 24 + tz))
    srise = swe.rise_trans((jd + 1) - tz / 24, swe.SUN, geopos=(lon, lat, 0), rsmi=_rise_flags + swe.CALC_RISE)[1][0]
    night_dur = (srise - sset)
    for i in range(1, 9):
        end_times.append(to_dms((sset + (i * night_dur) / 8 - jd) * 24 + tz))
    return end_times

def trikalam(jd, place, option='rahu'):
    lat, lon, tz = place
    tz = place.timezone
    srise = swe.rise_trans(jd - tz / 24, swe.SUN, geopos=(lon, lat, 0), rsmi=_rise_flags + swe.CALC_RISE)[1][0]
    sset = swe.rise_trans(jd - tz / 24, swe.SUN, geopos=(lon, lat, 0), rsmi=_rise_flags + swe.CALC_SET)[1][0]
    day_dur = (sset - srise)
    weekday = vaara(jd)
    offsets = {'rahu': [0.875, 0.125, 0.75, 0.5, 0.625, 0.375, 0.25],
               'gulika': [0.75, 0.625, 0.5, 0.375, 0.25, 0.125, 0.0],
               'yamaganda': [0.5, 0.375, 0.25, 0.125, 0.0, 0.75, 0.625]}
    start_time = srise + day_dur * offsets[option][weekday]
    end_time = start_time + 0.125 * day_dur
    start_time = (start_time - jd) * 24 + tz
    end_time = (end_time - jd) * 24 + tz
    return [to_dms(start_time), to_dms(end_time)]

rahu_kalam = lambda jd, place: trikalam(jd, place, 'rahu')
yamaganda_kalam = lambda jd, place: trikalam(jd, place, 'yamaganda')
gulika_kalam = lambda jd, place: trikalam(jd, place, 'gulika')

def abhijit_muhurta(jd, place):
    lat, lon, tz = place
    tz = place.timezone
    srise = swe.rise_trans(jd - tz / 24, swe.SUN, geopos=(lon, lat, 0), rsmi=_rise_flags + swe.CALC_RISE)[1][0]
    sset = swe.rise_trans(jd - tz / 24, swe.SUN, geopos=(lon, lat, 0), rsmi=_rise_flags + swe.CALC_SET)[1][0]
    day_dur = (sset - srise)
    start_time = srise + 7 / 15 * day_dur
    end_time = srise + 8 / 15 * day_dur
    return [(start_time - jd) * 24 + tz, (end_time - jd) * 24 + tz]

def planetary_positions(jd, place):
    jd_ut = jd - place.timezone / 24.
    positions = []
    for planet in planet_list:
        if planet != swe.KETU:
            planet_long = planet_longitude(jd_ut, planet)
        else:
            planet_long = ketu(planet_longitude(jd_ut, swe.RAHU))
        constellation = int(planet_long / 30)
        coordinates = to_dms(planet_long % 30)
        positions.append([planet, constellation, coordinates, nakshatra_pada(planet_long)])
    return positions

def ascendant(jd, place):
    lat, lon, tz = place
    jd_utc = jd - (tz / 24.)
    set_ayanamsa_mode()
    lagna = swe.houses_ex(jd_utc, lat, lon, flags=swe.FLG_SIDEREAL)[1][0]
    constellation = int(lagna / 30)
    coordinates = to_dms(lagna % 30)
    reset_ayanamsa_mode()
    return [constellation, coordinates, nakshatra_pada(lagna)]

def navamsa_from_long(longitude):
    one_pada = (360 / (12 * 9))
    one_sign = 12 * one_pada
    signs_elapsed = longitude / one_sign
    fraction_left = signs_elapsed % 1
    return int(fraction_left * 12)

def navamsa(jd, place):
    jd_utc = jd - place.timezone / 24.
    positions = []
    for planet in planet_list:
        if planet != swe.KETU:
            nirayana_long = planet_longitude(jd_utc, planet)
        else:
            nirayana_long = ketu(planet_longitude(jd_utc, swe.RAHU))
        positions.append([planet, navamsa_from_long(nirayana_long)])
    return positions
