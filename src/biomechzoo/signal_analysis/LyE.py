from typing import Dict
import numpy as np
import numpy.matlib as nmp
import numpy.polynomial.polynomial as poly
import scipy.sparse as sp
from .symmetry import symmetry
from .signal_inputs import three_axis_signal


# Some hard coded variables
# Bruijn, S. M., Ten Kate, W. R. T., Faber, G. S., Meijer, O. G., Beek, P. J., & van Dieën, J. H. (2010).
# Estimating dynamic gait stability using data from non-aligned inertial sensors.
# Annals of biomedical engineering, 38, 2588-2593.
WS = 10


def LyE_R(data: Dict, ch:list):
    """
    Estimate short- and long-term divergence exponents using Rosenstein's method.

    Parameters
    ----------
    data : dict
        Biomechanical data dictionary containing the input signals and video
        sampling frequency.
    ch : list[str]
        Names of the three signal channels used to calculate the vector norm
        and signal period.

    Returns
    -------
    lds : list[float]
        Short- and long-term divergence slopes. The short-term slope is fitted
        over the first half of a signal period; the long-term slope is fitted
        over the interval from four signal periods to the analysis window.
    average_log_divergence : np.ndarray
        Average log-divergence curve used to estimate the slopes.

    Notes
    -----
    Adapted from Sarwar, S., Likens, A., Stergiou, N., & Mastorakis, S.
    (2023). *A Nonlinear Analysis Software Toolkit for Biomechanical Data*.
    arXiv:2311.06723. The results were internally compared with MATLAB's
    built-in Lyapunov exponent function.
    """
    signal, _ = three_axis_signal(data, ch)
    norm = np.linalg.norm(signal, axis=1)
    ami = AMI_Stergiou(norm, 30)
    fs = data["zoosystem"]["Video"]["Freq"]
    tau = int(ami[0][0][0])
    [dE, dim] = FNN(norm, tau, 12, 15, 2, 1)

    X = np.array(norm, ndmin=2)
    r, c = np.shape(X)
    if r > c:
        X = np.copy(X.transpose())

    # Checks if a multidimentional array was entered as X.
    if np.size(X, axis=0) > 1:
        M = np.shape(X)[1]
        Y = X
    else:
        # Calculate useful size of data
        N = np.shape(X)[1]
        M = N - (dim - 1) * tau

        Y = np.zeros((M, dim))
        for j in range(dim):
            Y[:, j] = X[:, 0 + j * tau:M + j * tau]

    # Find nearest neighbors
    IND2 = np.zeros((1, M), dtype=int)
    for i in range(M):
        # Find nearest neighbor.
        Yinit = nmp.repmat(Y[i], M, 1)
        Ydiff = (Yinit - Y[0:M, :]) ** 2
        Ydisti = np.sqrt(np.sum(Ydiff, axis=1))

        # Exclude points too close based on dominant fsuency.
        range_exclude = np.arange(round((i + 1) - tau * 0.8 - 1), round((i + 1) + tau * 0.8))
        range_exclude = range_exclude[(range_exclude >= 0) & (range_exclude < M)]
        Ydisti[range_exclude] = 1e5

        # find minimum distance point for first pair
        IND2[0, i] = np.argsort(Ydisti)[0]

    out = np.vstack((np.arange(M), np.ndarray.flatten(IND2)))

    # Calculate distances between matched pairs.
    DM = np.zeros((M, M))

    IND2len = np.shape(IND2)[1]

    for i in range(IND2len):
        # The data can only be propagated so far from the matched pair.
        EndITL = M - IND2[:, i][0]
        if (M - IND2[:, i][0]) > (M - i):
            EndITL = M - i

        # Finds the distance between the matched paris and their propagated
        # points to the end of the useable data.
        DM[0:EndITL, i] = np.sqrt(
            np.sum((Y[i:EndITL + i, :] - Y[IND2[:, i][0]:EndITL + IND2[:, i][0], :]) ** 2, axis=1))

    # Calculates the average line divergence.
    r, _ = np.shape(DM)

    AveLnDiv = np.zeros(len(DM))
    # NOTE: MATLAB version does not preallocate AveLnDiv, we could preallocate that.
    for i in range(r):
        distanceM = DM[i, :]
        if np.sum(distanceM) != 0:
            AveLnDiv[i] = np.mean(np.log(distanceM[distanceM > 0]))

    out = np.vstack((out, AveLnDiv))
    AveLnDiv = AveLnDiv


    # determine the relevant period of the signal. In our case, the stride frequency
    _, _, d_2, _, _ = symmetry(data, ch)

    period = d_2 / fs
    ws = round(WS * fs)
    # find the least square fit
    L1 = int(0.5 * period * fs)
    L1 = L1

    # np.arange(1 / fs, L1, 1 / fs)
    # Ps = poly.polyfit(np.arange(1 / fs, L1 / fs, 1 / fs), AveLnDiv[1:L1], 1)
    np.arange(1 / fs, L1, 1 / fs)
    Ps = poly.polyfit(np.arange(1 / fs, L1 / fs, 1 / fs), AveLnDiv[1:L1], 1)
    if ws > 4 * period * fs:
        L2 = int(4 * period * fs)
        L2 = L2

        if len(np.arange(L2 / fs, ws / fs, 1 / fs)) == len(AveLnDiv[L2:ws]):
            Pl = poly.polyfit(np.arange(L2 / fs, ws / fs, 1 / fs), AveLnDiv[L2:ws], 1)
        elif len(np.arange(L2 / fs, ws / fs, 1 / fs)) - len(AveLnDiv[L2:ws]) == 1:
            Pl = poly.polyfit(np.arange(L2 / fs, ws / fs, 1 / fs), AveLnDiv[L2:ws + 1], 1)
        else:
            Pl = [np.nan, np.nan]

    lds = [Ps[1], Pl[1]]

    # Ys = poly.polyval(np.arange(1 / fs, L1 / fs, 1 / fs), Ps)
    # Yl = poly.polyval(np.arange(L2 / fs, ws / fs, 1 / fs), Pl)
    #
    # x_as = np.arange(1 / fs, ws / fs, 1 / fs)
    # plt.plot(x_as, AveLnDiv[:ws - 1])
    #
    # plt.plot(np.arange(1 / fs, L1 / fs, 1 / fs), Ys, 'm')
    # plt.plot(np.arange(L2 / fs, ws / fs, 1 / fs), Yl, 'r')
    #
    # figname = "Subject{}_{}".format(
    #     data['zoosystem']['subj_no'], data['zoosystem']['surface']
    # )
    # plt.savefig("./Figures/LyE_R/{}.jpeg".format(figname))
    #
    # plt.close()
    # del figname
    return lds, AveLnDiv


# embedded functions
def AMI_Stergiou(data, L, to_matlab=False, n_bins=0):
    """
    Calculate average mutual information (AMI) using histogram binning.

    With an integer ``L``, calculate AMI for lags from zero to ``L - 1`` and
    identify lag candidates. With ``L`` supplied as an array or list, calculate
    the AMI between the two input signals.

    Parameters
    ----------
    data : array_like
        One-dimensional input time series. In paired-signal mode, this is the
        first signal.
    L : int or array_like
        Maximum lag in single-series mode, or the second signal in
        paired-signal mode.
    to_matlab : bool, optional
        In paired-signal mode, import the MATLAB package before returning the
        AMI value. The return value remains a Python scalar. Defaults to
        ``False``.
    n_bins : int, optional
        Number of histogram bins in single-series mode. If zero, estimate the
        bin count using Scott's rule. Defaults to zero.

    Returns
    -------
    tuple[np.ndarray, np.ndarray] or float
        In single-series mode, return ``(tau, v_AMI)``. ``tau`` contains rows
        of lag and AMI values for detected lag candidates, and ``v_AMI``
        contains the lag and AMI series. In paired-signal mode, return the
        scalar AMI between ``data`` and ``L``.

    Raises
    ------
    ValueError
        If paired signals have different lengths or ``L`` is neither an
        integer nor an array-like signal.

    Notes
    -----
    The single-series calculation uses AMI to select a time delay for phase
    space reconstruction. The paired-signal mode requires inputs of equal
    length.

    Copyright 2020 Nonlinear Analysis Core, Center for Human Movement
    Variability, University of Nebraska at Omaha.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are
    met:

    1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.
    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.
    3. Neither the name of the copyright holder nor the names of its
       contributors may be used to endorse or promote products derived from
       this software without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
    IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
    THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
    PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
    CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
    EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
    PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
    PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
    LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
    NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    """
    eps = np.finfo(float).eps  # smallest floating point value

    if isinstance(L, int):
        N = len(data)

        data = np.array(data)

        if n_bins == 0:
            bins = np.ceil((np.max(data) - np.min(data)) / (3.49 * np.nanstd(data * N ** (-1 / 3), axis=0)))
        else:
            bins = n_bins

        bins = int(bins)

        data = data - min(data)  # make all data points positive
        y = np.floor(data / (np.max(data) / (bins - eps)))
        y = np.array(y,
                     dtype=int)  # converts the vector of double vals from data2 into a list of integers from 0 to overlap (where overlap is N-L).

        v = np.zeros((L, 1))  # preallocate the vector
        overlap = N - L
        increment = 1 / overlap

        pA = sp.csr_matrix((np.full(overlap, increment), (y[0:overlap], np.ones(overlap, dtype=int)))).toarray()[:, 1]

        v = np.zeros((2, L))

        for lag in range(L):  # used to be from 0:L-1 (BS)
            v[0, lag] = lag

            pB = sp.csr_matrix(
                (np.full(overlap, increment), (y[lag:overlap + lag], np.ones(overlap, dtype=int)))).toarray()[:, 1]
            # find joint probability p(A,B)=p(x(t),x(t+time_lag))
            pAB = sp.csr_matrix((np.full(overlap, increment), (y[0:overlap], y[lag:overlap + lag])))

            (A, B) = np.nonzero(pAB)
            AB = pAB.data

            v[1, lag] = np.sum(
                np.multiply(AB, np.log2(np.divide(AB, np.multiply(pA[A], pB[B])))))  # Average Mutual Information

        tau = np.array(np.full((L, 2), -1, dtype=float))

        j = 0
        for i in range(v.shape[1] - 1):  # Finds first minimum
            if v[1, i - 1] >= v[1, i] and v[1, i] <= v[1, i + 1]:
                ami = v[1, i]
                tau[j, :] = np.array([i, ami])
                j += 1

        tau = tau[:j]  # only include filled in data.

        initial_AMI = v[1, 0]
        for i in range(v.shape[1]):  # Finds first AMI value that is 20% initial AMI
            if v[1, i] < (0.2 * initial_AMI):
                tau[0, 1] = i
                break

        v_AMI = v

        return (tau, v_AMI)
    elif isinstance(L, np.ndarray) or isinstance(L, list):
        x = data if isinstance(data, np.ndarray) else np.array(data)
        y = L if isinstance(L, np.ndarray) else np.array(L)

        if len(x) != len(y):
            raise ValueError('X and Y must be the same size.')

        increment = 1 / len(y)
        one = np.ones(len(y), dtype=int)

        bins1 = np.ceil((max(x) - min(x)) / (3.49 * np.nanstd(x) * len(x) ** (-1 / 3)))  # Scott 1979
        bins2 = np.ceil((max(y) - min(y)) / (3.49 * np.nanstd(y) * len(y) ** (-1 / 3)))  # Scott 1979
        x = x - min(x)  # make all data points positive
        x = np.floor(x / (max(x) / (bins1 - eps)))  # scaling the data
        y = y - min(y)  # make all data points positive
        y = np.floor(y / (max(y) / (bins2 - eps)))  # scaling the data

        x = np.array(x, dtype=int)
        y = np.array(y, dtype=int)

        increment = np.full(len(y), increment)
        pA = sp.csr_matrix((increment, (x, one))).toarray()[:, 1]
        pB = sp.csr_matrix((increment, (y, one))).toarray()[:, 1]
        pAB = sp.csr_matrix((increment, (x, y)))
        (A, B) = np.nonzero(pAB)
        AB = pAB.data
        ami = np.sum(np.multiply(AB, np.log2(np.divide(AB, np.multiply(pA[A], pB[B])))))

        if to_matlab:
            import matlab
            return ami
        else:
            return ami
    else:
        raise ValueError('Invalid input, read documentation for input options.')


def FNN(data, tau, MaxDim, Rtol, Atol, speed):
    """
    Estimate the embedding dimension using the false nearest neighbors method.

    Parameters
    ----------
    data : array_like
        One-dimensional time series.
    tau : int
        Time delay used to reconstruct the phase space.
    MaxDim : int
        Maximum embedding dimension to evaluate.
    Rtol : float
        Relative distance threshold for the first false-neighbor criterion.
        A value of 15 is commonly used.
    Atol : float
        Attractor-size threshold for the second false-neighbor criterion.
        A value of 2 is commonly used.
    speed : int
        If 1, stop when a minimum embedding dimension is detected. If 0,
        evaluate through ``MaxDim`` before selecting a dimension.

    Returns
    -------
    tuple[np.ndarray, int]
        ``(dE, dimension)`` where ``dE`` contains the false-neighbor
        proportions for each evaluated dimension, and ``dimension`` is the
        selected embedding dimension, using one-based indexing.

    Notes
    -----
    Reference: Kennel, M. B., Brown, R., & Abarbanel, H. D. I. (1992).
    Determining embedding dimension for phase-space reconstruction using a
    geometrical construction. *Physical Review A*, 45(6), 3403-3411.
    """
    n = len(data) - tau * MaxDim
    data_array = np.array(data)
    RA = np.std(data_array)

    z = np.array([data_array[0:n]])
    y = np.array([[]])

    m_search = 2

    indx = np.array(np.arange(0, n))
    dim = np.array([])

    dE = np.zeros((MaxDim, 1))

    for j in range(MaxDim):
        # y = np.array([y,z]) # adds additional dimension
        if j == 0:
            y = np.array([np.append(y, z)])
        else:
            y = np.array(np.vstack([y, z]))
        z = np.array([data_array[tau * (j + 1):n + tau * (j + 1)]])
        L = np.zeros((n))

        (y_model, z_model, sort_list, node_list) = kd_part(y, z, 512)

        for i in range(len(indx)):
            yq = np.array(y[:, indx[i]])  # set up next point to look at

            b_upper = np.inf * np.ones(np.size(yq))
            b_lower = np.negative(b_upper)

            pqd = np.inf * np.ones((1, m_search))
            pqr = np.array([])
            pqz = np.array([])
            L_done = 0

            # A couple returning variables are not necessary. Check documentation of kd_search to see what they are.
            (pqd, y_model, z_model, _, _, pqz, _, _, sort_list, node_list) = kd_search(0, m_search, yq, pqd, y_model,
                                                                                       z_model, L_done, pqr, pqz,
                                                                                       b_upper, b_lower, sort_list,
                                                                                       node_list)

            distance = pqz[0] - pqz[1]

            if np.abs(distance) > pqd[1] * Rtol:
                L[i] = 1

            if np.sqrt(pqd[1] ** 2 + distance ** 2) / RA > Atol:
                L[i] = 1

        dE[j] = np.sum(L) / n

        if speed == 1:
            if j >= 2 and ((dE[j - 2] > dE[j - 1] and (dE[j - 1] < dE[j]))):
                dim = j - 1
                break
            if j >= 1 and np.abs(dE[j] - dE[j - 1]) <= 0.001:
                dim = j - 1
                break
            if dE[j] == 0:
                dim = j
                break

    if speed == 0:
        for i in range(len(dE)):
            if np.abs(dE[i - 1] - dE[i]) <= 0.001:
                dim = i - 1
                break
            try:  # In the case of where the code reaches to len(dE) - 1 and attempts to get dE[len(dE)], which causes an IndexError.
                if (dE[i] == 0) or ((dE[i - 1] > dE[i] and (dE[i] < dE[i + 1]))):
                    dim = i
                    break
            except:
                break

    if np.size(dim) == 0:
        dim = MaxDim - 1
        print('No dimension found, dim set to MaxDim\n')

    # +1 because we started from zero and not one. Might change this in the future
    return (dE, dim + 1)


def kd_part(y_in, z_in, bin_size):
    """
    Partition phase-space data into a k-d tree for nearest-neighbor searches.

    Parameters
    ----------
    y_in : np.ndarray
        Phase-space data with dimensions arranged as rows and observations as
        columns.
    z_in : np.ndarray
        Data associated with each observation in ``y_in``, arranged with
        observations as columns.
    bin_size : int
        Maximum number of observations in a terminal tree node.

    Returns
    -------
    tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
        ``(y_model, z_model, sort_list, node_list)``. The first two arrays
        contain the partitioned data. ``sort_list`` stores each node's split
        dimension and boundary; ``node_list`` stores the observation range
        and child-node indices for each node.

    Notes
    -----
    The partitioning algorithm is based on Bentley, J. L., & Friedman, J. H.
    (1979), *Data Structures for Range Searching*, and Friedman, J. H.,
    Bentley, J. L., & Finkel, R. A. (1977), *An Algorithm for Finding Best
    Matches in Logarithmic Expected Time*.
    """
    y_model = y_in
    z_model = z_in

    # d: dimension of phase space
    # n_y: number of points to put into partitioned database

    (d, n_y) = y_model.shape

    # Set up first node...
    node_list = np.array([[0, n_y, 0, 0]])
    sort_list = np.array([[0, 0]], dtype=float)

    node = 0
    last = 0

    while node <= last:  # check if the node can be divided
        segment = np.array([np.arange(node_list[node, 0], node_list[node, 1])])
        # previously: [node_list[node,1]:node_list[node,2]]
        rg = np.amax(y_model, axis=1) - np.amin(y_model, axis=1)  # previously i and segment were swapped

        # segment.shape[1] is the length of the segment (specifically the length of the row)
        if np.max(rg) > 0 and segment.shape[1] >= bin_size:  # it is divisible

            index = np.argsort(rg)
            yt = np.squeeze(y_model[:, segment], axis=1)  # swapped : and segment
            zt = np.squeeze(z_model[:, segment], axis=1)
            y_index = np.argsort(yt[index[d - 1]])
            y_sort = np.sort(yt[index[d - 1]])  # swapped : and index[d],

            # estimate where the cut should go
            _, tlen = yt.shape

            if np.fmod(tlen, 2):  # yt has an odd number of elements
                cut = y_sort[int((tlen + 1) / 2)]
            else:  # yt has an even number of elements
                cut = (y_sort[int(tlen / 2)] + y_sort[int(tlen / 2 + 1)]) / 2
                # end of the median calculation

            L = y_sort <= cut

            if np.sum(L) == tlen:  # then the right node will be empty...
                L = y_sort < cut  # ...so use a slightly different boundary
                cut = (cut + np.max(y_sort[L])) / 2
                # end of the cut adjustment

                # adjust the order of the data
            y_model[:, segment] = np.expand_dims(yt[:, y_index], axis=1)
            z_model[:, segment - 1] = zt[:, y_index]

            # mark this as a non-terminal node
            sort_list[node, :] = [index[d - 1], cut]
            node_list[node, 2] = last + 1
            node_list[node, 3] = last + 2
            last = last + 2

            # add the information for the new nodes
            node_list = np.vstack([node_list, [segment[0][0], segment[0][0] + np.sum(L) - 1, 0, 0]])
            node_list = np.vstack([node_list, [segment[0][0] + np.sum(L), segment[0][tlen - 1], 0, 0]])
            sort_list = np.vstack([sort_list, [[0, 0], [0, 0]]])

        # end of the splitting process

        node += 1
        # end of the while loop

    return (y_model, z_model, sort_list, node_list)


def kd_search(node, m_search, yq, pqd, y_model, z_model, L_done, pqr, pqz, b_upper, b_lower, sort_list, node_list):
    """
    Search a k-d tree for the nearest neighbors of a query point.

    Parameters
    ----------
    node : int
        Index of the current tree node.
    m_search : int
        Maximum number of nearest neighbors to retain.
    yq : np.ndarray
        Query point in phase space.
    pqd : np.ndarray
        Current nearest-neighbor distances, initialized with infinite values.
    y_model : np.ndarray
        Partitioned phase-space data.
    z_model : np.ndarray
        Data associated with the points in ``y_model``.
    L_done : int
        Search-completion flag. A nonzero value indicates that the search
        can stop.
    pqr : np.ndarray
        Current nearest-neighbor phase-space points.
    pqz : np.ndarray
        Data values associated with the current nearest neighbors.
    b_upper, b_lower : np.ndarray
        Upper and lower bounds of the current tree region.
    sort_list : np.ndarray
        Split dimensions and partition boundaries for the tree nodes.
    node_list : np.ndarray
        Observation ranges and child-node indices for the tree nodes.

    Returns
    -------
    tuple
        Updated values in this order: ``pqd``, ``y_model``, ``z_model``,
        ``L_done``, ``pqr``, ``pqz``, ``b_upper``, ``b_lower``, ``sort_list``,
        and ``node_list``.
    """
    if L_done == 1:
        return (pqd, y_model, z_model, L_done, pqr, pqz, b_upper, b_lower, sort_list, node_list)

    if node_list[node, 2] == 0:  # it's a terminal node, so...
        # first, compute the distances...
        yi = node_list[node, 0:2]  # index bounds of all y_model to consider
        yt = y_model[:, yi[0]:yi[1]]
        zt = z_model[:, yi[0]:yi[1]]

        d = len(yq)  # get the dimension

        yq1 = yq  # using this to swap the yq array back to a row vector
        yq = yq[:, np.newaxis]  # column vector

        dist = np.sqrt(np.sum((yt[0:d, :] - yq[0:d]) ** 2, axis=0))

        yq = yq1

        # and then sort them and load pqd, pqr, and pqz

        # distances ^2
        pqd = np.append(dist, pqd)
        pqr = np.append(yt, pqr)
        pqz = np.append(zt, pqz)

        index = np.argsort(pqd)  # distances sorted indexes
        pqd = np.sort(pqd)  # distances sorted

        length = pqz.shape[0]

        if len(index) > length:  # to avoid indexing out of bounds
            pqr = pqr[index[0:len(pqz)]]
            pqz = pqz[index[0:len(pqz)]]
        else:  # if index is <= length then we're okay to use the entirety of its length
            pqr = pqr[index]
            pqz = pqz[index]
        # keep only the first m_search points
        if len(pqd) > m_search:
            pqd = pqd[0:m_search]

        length = pqz.shape[0]

        # most of the time this is true
        if length > m_search:
            pqr = pqr[0:m_search]
            pqz = pqz[0:m_search]

        # m_search-1 to not cause indexing issues
        if any((np.abs(yq - b_lower) <= pqd[m_search - 1]) | (np.abs(yq - b_upper) <= pqd[m_search - 1])):
            L_done = 1

        return (pqd, y_model, z_model, L_done, pqr, pqz, b_upper, b_lower, sort_list, node_list)
    else:  # it's not a terminal node, so search a little deeper
        disc = int(sort_list[node, 0])
        part = sort_list[node, 1]

        if yq[disc] <= part:  # determine which child node to go to

            temp = b_upper[disc]
            b_upper[disc] = part
            #         [pqd]=kdsearch(node_list(node,3),m_search,yq,pqd)
            (pqd, y_model, z_model, L_done, pqr, pqz, b_upper, b_lower, sort_list, node_list) = kd_search(
                node_list[node, 2], m_search, yq, pqd, y_model, z_model, L_done, pqr, pqz, b_upper, b_lower, sort_list,
                node_list)
            b_upper[disc] = temp
        else:
            temp = b_lower[disc]
            b_lower[disc] = part
            #         [pqd]=kdsearch(node_list(node,4),m_search,yq,pqd)
            (pqd, y_model, z_model, L_done, pqr, pqz, b_upper, b_lower, sort_list, node_list) = kd_search(
                node_list[node, 3], m_search, yq, pqd, y_model, z_model, L_done, pqr, pqz, b_upper, b_lower, sort_list,
                node_list)
            b_lower[disc] = temp

        if L_done:
            return (pqd, y_model, z_model, L_done, pqr, pqz, b_upper, b_lower, sort_list, node_list)

        if yq[disc] <= part:  # determine whether other child node needs to be searched
            temp = b_lower[disc]
            b_lower[disc] = part

            L = overlap(yq, m_search, pqd, b_upper, b_lower)
            if L == 1:
                #             [pqd]=kdsearch(node_list(node,4),m_search,yq,pqd);
                (pqd, y_model, z_model, L_done, pqr, pqz, b_upper, b_lower, sort_list, node_list) = kd_search(
                    node_list[node, 4], m_search, yq, pqd, y_model, z_model, L_done, pqr, pqz, b_upper, b_lower,
                    sort_list, node_list)

                b_lower[disc] = temp
        else:
            temp = b_upper[disc]
            b_upper[disc] = part

            L = overlap(yq, m_search, pqd, b_upper, b_lower)
            if L == 1:
                #             [pqd]=kdsearch(node_list(node,3),m_search,yq,pqd);
                (pqd, y_model, z_model, L_done, pqr, pqz, b_upper, b_lower, sort_list, node_list) = kd_search(
                    node_list[node, 3], m_search, yq, pqd, y_model, z_model, L_done, pqr, pqz, b_upper, b_lower,
                    sort_list, node_list)

                b_upper[disc] = temp

        if L_done:
            return (pqd, y_model, z_model, L_done, pqr, pqz, b_upper, b_lower, sort_list, node_list)

    return (pqd, y_model, z_model, L_done, pqr, pqz, b_upper, b_lower, sort_list, node_list)


def overlap(yq, m_search, pqd, b_upper, b_lower):
    """
    Check whether a query point can overlap the current k-d tree region.

    The check compares the squared distance from ``yq`` to the bounded region
    with the distance to the current ``m_search``-th nearest neighbor.

    Parameters
    ----------
    yq : np.ndarray
        Query point in phase space.
    m_search : int
        Number of nearest neighbors being retained.
    pqd : np.ndarray
        Sorted nearest-neighbor distances.
    b_upper, b_lower : np.ndarray
        Upper and lower bounds of the current tree region.

    Returns
    -------
    int
        ``1`` if the region may contain a closer neighbor, otherwise ``0``.

    Notes
    -----
    The bounding-region search is based on Bentley, J. L., & Friedman, J. H.
    (1979), *Data Structures for Range Searching*, and Friedman, J. H.,
    Bentley, J. L., & Finkel, R. A. (1977), *An Algorithm for Finding Best
    Matches in Logarithmic Expected Time*.
    """
    # indexing with m_search = 2 on a 2 size numpy array causes errors so it is pqd[m_search-1]
    dist = pqd[m_search - 1] ** 2
    sum = 0

    for i in range(len(yq)):

        if yq[i] < b_lower[i]:
            sum = sum + (yq[i] - b_lower[i]) ** 2
            if sum > dist:
                L = 0
                return L
            # end of the sum > dist
        elif yq[i] > b_upper[i]:
            sum = sum + (yq[i] - b_upper[i]) ** 2
            if sum > dist:
                L = 0
                return L
            # end of the sum > dist if
        # end of the yq(i) <> a bound if
    # end of the i loop

    L = 1

    return L
