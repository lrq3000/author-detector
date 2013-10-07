#!/usr/bin/env python
# encoding: utf-8
#
# AuthorDetector
# Copyright (C) 2013 Larroque Stephen
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

## @package salience
#
# Compute the neighbouring and global salience score

from authordetector.validator.basevalidator import BaseValidator
import pandas as pd
import numpy as np

## Salience
#
# Compute the local (neighbouring) and global salience score
# The salience is a score that shows how clear the model defines the discrimination between the good class and the others
class Salience(BaseValidator):

    ## @var config
    # A reference to a ConfigParser object, already loaded

    ## @var parent
    # A reference to the parent object (Runner)

    constraints = {
        'after': 'detector' # Salience should be computed only after detection
    }

    ## Constructor
    # @param config An instance of the ConfigParser class
    def __init__(self, config=None, parent=None, *args, **kwargs):
        return BaseValidator.__init__(self, config, parent, *args, **kwargs)

    # Compute the neighbouring and global salience score
    # The salience is a score that shows how clear the model defines the discrimination between the good class and the others
    # Note: the salience is NOT a measure of accuracy. The model can be completely mistaken and detect a totally wrong class/author and still have a high salience.
    # @param Result_details The detailed results of detection (containing the exact values of detection, not just a binary True/False but a Real/Float value).
    # @param ValidationScore Already existing ValidationScore dict to surcharge it if several model validators are used at once.
    # @return dict A dict containing ValidationScore
    def validate(self, Result_details=None, ValidationScore=None, *args, **kwargs):
        if Result_details is None:
            print("Error: no details for results, cannot compute the salience!")
            return

        # Convert into a Dataframe (easier to do computations)
        rd = pd.DataFrame(Result_details)

        # Create/Setup ValidationScore
        if ValidationScore is None:
            ValidationScore = dict()
        ValidationScore['Salience'] = dict() # Create an entry for Salience in ValidationScore

        # For each result details (of each text that was detected)
        for idx, details in Result_details.iteritems():
            #txtconfig = self.parent.reader.get_params(idx)
            # Error if the config was not set properly
            #if not 'label' in txtconfig:
            #    ValidationScore['Salience'][idx] = None
            #    print("Error: no 'label' variable defined for text %s, will skip this text." % idx)
            #else:
            rdc = rd.ix[:,idx]
            max_pred = rdc.max()
            max_neighbor = rdc.ix[rdc != max_pred].max()
            mean_neighbors = rdc.ix[rdc != max_pred].mean()
            local_salience = (max_pred - max_neighbor) / np.min([max_pred, max_neighbor])
            global_salience = (max_pred - mean_neighbors) / np.min([max_pred, mean_neighbors])
            ValidationScore['Salience'][idx] = {'Local': local_salience, 'Global': global_salience}
            print("Salience for text %s: local %s - global %s" % (idx, local_salience, global_salience))

        # Return the resulting variables (in a dict of vars)
        return {'ValidationScore': ValidationScore}
